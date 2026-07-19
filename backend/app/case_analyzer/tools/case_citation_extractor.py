import logging
import unicodedata
from pathlib import PurePath

import logfire
from agents import Agent, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..runner import run_agent
from ..validation import has_navigation_evidence, is_placeholder_text, validate_case_citation
from .document_nav import NAV_TOOLS, DocumentContext
from .models import CaseCitationOutput, StepResult

logger = logging.getLogger(__name__)

_EXCERPT_CHARS = 4000
_FILENAME_SOURCE_LOCATION = "original filename"
_MAX_REASONING_CHARS = 300


def _citation_excerpts(text: str) -> str:
    """Return bounded verbatim excerpts from the likely citation locations."""
    if len(text) <= _EXCERPT_CHARS * 2:
        return f"[document beginning and end]\n{text}"
    return f"[document beginning]\n{text[:_EXCERPT_CHARS]}\n\n[document end]\n{text[-_EXCERPT_CHARS:]}"


def _normalize_identifier(text: str) -> str:
    """Normalize identifier separators without encoding jurisdiction-specific formats."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _filename_identifier_candidates(file_name: str | None) -> tuple[str, ...]:
    """Find strong identifier-shaped filename segments without assuming a jurisdiction."""
    if not file_name:
        return ()

    candidates: list[str] = []
    for raw_segment in PurePath(file_name).stem.split():
        segment = raw_segment.strip("()[]{}.,;:")
        digit_count = sum(character.isdigit() for character in segment)
        separator_count = sum(not character.isalnum() for character in segment)
        if any(character.isalpha() for character in segment) and digit_count >= 3 and separator_count >= 2:
            candidates.append(segment)
    return tuple(candidates)


def _citation_appends_date_to_candidate(citation: str, candidates: tuple[str, ...]) -> bool:
    normalized_citation = _normalize_identifier(citation)
    for candidate in candidates:
        normalized_candidate = _normalize_identifier(candidate)
        suffix = normalized_citation.removeprefix(normalized_candidate)
        if suffix != normalized_citation and suffix.isdigit() and 6 <= len(suffix) <= 8:
            return True
    return False


def _citation_copies_descriptive_filename(file_name: str | None, citation: str) -> bool:
    """Detect page-title filenames returned wholesale instead of a canonical identifier."""
    if not file_name:
        return False
    stem = PurePath(file_name).stem
    alpha_word_count = sum(any(character.isalpha() for character in word) for word in stem.split())
    normalized_stem = _normalize_identifier(stem)
    normalized_citation = _normalize_identifier(citation)
    return (
        alpha_word_count >= 4
        and len(normalized_citation) >= 20
        and normalized_citation in normalized_stem
        and len(normalized_citation) / len(normalized_stem) >= 0.7
    )


def _validate_citation_against_document(
    doc_ctx: DocumentContext,
    output: CaseCitationOutput,
    tool_names: frozenset[str],
) -> str | None:
    """Require every positive citation to be traceable to verbatim document text."""
    candidates = _filename_identifier_candidates(doc_ctx.file_name)
    if len(output.reasoning.strip()) > _MAX_REASONING_CHARS:
        return "Citation reasoning must be one short sentence about where the identifier was found."
    if _citation_copies_descriptive_filename(doc_ctx.file_name, output.case_citation):
        return (
            "The result copies a descriptive filename or page title rather than a canonical citation. Search the decision "
            "for the highest-priority identifier: an official neutral identifier such as ECLI, then an official reporter "
            "citation, then a docket or case number."
        )
    if is_placeholder_text(output.case_citation) and candidates:
        return (
            "The original filename contains strong identifier-shaped segment(s): "
            f"{', '.join(candidates)}. Re-examine them before returning 'NA'."
        )

    validation_error = validate_case_citation(output, tool_names)
    if validation_error is not None:
        return validation_error
    if is_placeholder_text(output.case_citation):
        return None

    assert output.source_text is not None
    assert output.source_location is not None
    if candidates and _citation_appends_date_to_candidate(output.case_citation, candidates):
        return "The case citation includes an adjacent decision date. Return only the identifier itself."
    if output.source_location.strip().casefold() == _FILENAME_SOURCE_LOCATION:
        if doc_ctx.file_name is None or output.source_text != doc_ctx.file_name:
            return "Filename evidence must copy the complete original filename exactly as source_text."
        normalized_citation = _normalize_identifier(output.case_citation)
        normalized_filename = _normalize_identifier(doc_ctx.file_name)
        if not normalized_citation or normalized_citation not in normalized_filename:
            return "The case citation cannot be traced to the original filename. Re-examine the supplied metadata."
        if candidates and normalized_citation not in {_normalize_identifier(candidate) for candidate in candidates}:
            return (
                "The filename-derived citation must correspond exactly to one identifier-shaped segment. "
                "Exclude adjacent dates or descriptive filename text."
            )
        if output.confidence == "high":
            return "A citation supported only by the original filename cannot have high confidence."
        return None

    if output.source_text not in doc_ctx.text:
        return "source_text is not a verbatim passage from the decision. Copy it exactly from the supplied document."
    source_was_supplied = (
        output.source_text in doc_ctx.text[:_EXCERPT_CHARS] or output.source_text in doc_ctx.text[-_EXCERPT_CHARS:]
    )
    if not source_was_supplied and not has_navigation_evidence(tool_names):
        return "The citation evidence is outside the supplied excerpts. Use a navigation tool to inspect that passage."
    return None


def _citation_prompt(
    doc_ctx: DocumentContext,
    legal_system: str,
    jurisdiction: str,
    fallback_reason: str | None = None,
) -> list[TResponseInputItem]:
    candidates = _filename_identifier_candidates(doc_ctx.file_name)
    candidate_text = ", ".join(candidates) if candidates else "[none detected]"
    fallback_text = ""
    if fallback_reason is not None:
        fallback_text = (
            "\n\nThe initial evidence-only result was inconclusive or invalid for this reason:\n"
            f"{fallback_reason}\nUse the navigation tools to inspect the rest of the decision before answering."
        )
    return [
        {
            "role": "user",
            "content": (
                f"Jurisdiction: {jurisdiction}\n"
                f"Legal System: {legal_system}\n\n"
                f"Original filename: {doc_ctx.file_name or '[not available]'}\n"
                f"Identifier-like filename segments: {candidate_text}\n\n"
                "Treat the filename and document excerpts as parallel evidence for this decision's identifier.\n\n"
                f"<court_decision_excerpts>\n{_citation_excerpts(doc_ctx.text)}\n</court_decision_excerpts>"
                f"{fallback_text}"
            ),
        },
    ]


async def extract_case_citation(
    doc_ctx: DocumentContext,
    legal_system: str,
    jurisdiction: str,
) -> StepResult[CaseCitationOutput]:
    """Extract case citation from court decision text."""
    with logfire.span("case_citation"):
        instructions = (
            "Extract the canonical case citation as it appears in the court decision. "
            "Treat the original filename and the supplied beginning/end excerpts as parallel evidence. Compare them before "
            "answering. Rank identifiers in this order: (1) an official neutral identifier such as ECLI or its "
            "jurisdictional equivalent, (2) an official reporter citation, (3) a docket or case number, and only then "
            "(4) filename metadata. Return only the highest-ranked identifier available for this decision. Never return a "
            "descriptive page title, court name, decision date, publication status, or party caption as the citation. "
            "If the filename and decision agree after separator normalization, prefer the exact identifier format printed "
            "in the decision and use high confidence. If only the filename identifies the decision, return its conventional form, "
            "copy the complete filename exactly into source_text, set source_location to 'original filename', and use "
            "medium or low confidence. File-safe underscores, dashes, and spaces may encode conventional separators. "
            "Use the document's own citation format and language verbatim — do not translate, "
            "expand, or reformat court names, abbreviations, or docket numbers. Prefer the short canonical identifier "
            "over the full case header with parties, judges, and dates. Distinguish this decision's identifier from "
            "citations to authorities in its reasoning. "
            "For a positive result, source_text must be the exact verbatim line or compact passage containing the "
            "citation, source_location must identify the excerpt or numbered paragraph, and identifier_type must be a "
            "generic description of the identifier. "
            "If no citation is present in either the decision text or a clearly identifying filename, return 'NA' with "
            "low confidence — do not infer or fabricate — and return null for source_text, source_location, and "
            "identifier_type. When navigation tools are available, use them before returning 'NA'. "
            "The reasoning must be one short sentence describing only where the identifier was found and, when relevant, "
            "whether the filename and document agree. Never discuss the decision's facts, legal issues, or merits."
        )
        initial_agent = Agent[DocumentContext](
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            tools=NAV_TOOLS[:0],
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        initial_step = await run_agent(
            initial_agent,
            input=_citation_prompt(doc_ctx, legal_system, jurisdiction),
            context=doc_ctx,
        )
        initial_error = _validate_citation_against_document(doc_ctx, initial_step.output, frozenset())
        if initial_error is None and not is_placeholder_text(initial_step.output.case_citation):
            return initial_step

        fallback_reason = initial_error or "No citation was identified from the filename and supplied excerpts."
        logger.info("Citation evidence pass requires navigation fallback: %s", fallback_reason)
        navigation_agent = Agent[DocumentContext](
            name="CaseCitationNavigationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(
            navigation_agent,
            input=_citation_prompt(doc_ctx, legal_system, jurisdiction, fallback_reason),
            context=doc_ctx,
            validate=lambda output, tool_names: _validate_citation_against_document(doc_ctx, output, tool_names),
        )
