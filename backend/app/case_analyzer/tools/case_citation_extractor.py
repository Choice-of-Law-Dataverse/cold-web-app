import logging
import unicodedata
from pathlib import PurePath

import logfire
from agents import Agent, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel
from pydantic import BaseModel, Field

from ..config import get_model, get_openai_client
from ..runner import run_agent
from ..validation import has_navigation_evidence, is_placeholder_text, validate_case_citation
from .document_nav import NAV_TOOLS, DocumentContext
from .models import CaseCitationOutput, StepResult

logger = logging.getLogger(__name__)

_EXCERPT_CHARS = 4000
_FILENAME_SOURCE_LOCATION = "original filename"


class _FilenameCitationCandidate(BaseModel):
    case_citation: str = Field(description="The conventional citation encoded by the filename segment")
    identifier_type: str = Field(description="A short generic category such as docket number or neutral citation")


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


def _validate_citation_against_document(
    doc_ctx: DocumentContext,
    output: CaseCitationOutput,
    tool_names: frozenset[str],
) -> str | None:
    """Require every positive citation to be traceable to verbatim document text."""
    candidates = _filename_identifier_candidates(doc_ctx.file_name)
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


def _validate_filename_candidate(
    candidates: tuple[str, ...],
    output: _FilenameCitationCandidate,
    _tool_names: frozenset[str],
) -> str | None:
    if is_placeholder_text(output.case_citation):
        return f"Select and normalize the decision identifier from: {', '.join(candidates)}."
    normalized_candidates = {_normalize_identifier(candidate) for candidate in candidates}
    if _normalize_identifier(output.case_citation) not in normalized_candidates:
        return (
            "The citation must correspond exactly to one supplied identifier segment after separator normalization. "
            "Exclude adjacent dates and descriptive filename text."
        )
    if not output.identifier_type.strip():
        return "Return a short generic identifier_type."
    return None


async def _extract_filename_citation(
    doc_ctx: DocumentContext,
    candidates: tuple[str, ...],
    jurisdiction: str,
) -> StepResult[CaseCitationOutput]:
    """Normalize a strong filename identifier without sending the decision text."""
    assert doc_ctx.file_name is not None
    candidate_text = ", ".join(candidates)
    agent = Agent[DocumentContext](
        name="FilenameCitationExtractor",
        instructions=(
            "Normalize an identifier-shaped filename segment into the conventional case or docket citation used in the "
            "stated jurisdiction. Preserve letters, digits, and language. Change only file-safe separators when needed. "
            "Exclude dates and descriptive text outside the supplied segment. Do not discuss the decision's facts, legal "
            "issues, or reasoning."
        ),
        output_type=_FilenameCitationCandidate,
        tools=NAV_TOOLS[:0],
        model=OpenAIResponsesModel(
            model=get_model("case_citation"),
            openai_client=get_openai_client(),
        ),
    )
    candidate_step = await run_agent(
        agent,
        input=(
            f"Jurisdiction: {jurisdiction}\n"
            f"Original filename: {doc_ctx.file_name}\n"
            f"Identifier-shaped segment(s): {candidate_text}\n"
            "Return the decision identifier only, without any adjacent decision date."
        ),
        context=doc_ctx,
        validate=lambda output, tool_names: _validate_filename_candidate(candidates, output, tool_names),
    )
    candidate = candidate_step.output
    output = CaseCitationOutput(
        case_citation=candidate.case_citation,
        source_text=doc_ctx.file_name,
        source_location=_FILENAME_SOURCE_LOCATION,
        identifier_type=candidate.identifier_type,
        confidence="medium",
        reasoning=f"Derived from the identifier-shaped filename segment '{candidate_text}'.",
    )
    validation_error = _validate_citation_against_document(doc_ctx, output, frozenset())
    if validation_error is not None:
        raise ValueError(validation_error)
    return StepResult(
        output=output,
        response_id=candidate_step.response_id,
        tool_names=candidate_step.tool_names,
    )


async def extract_case_citation(
    doc_ctx: DocumentContext,
    legal_system: str,
    jurisdiction: str,
) -> StepResult[CaseCitationOutput]:
    """Extract case citation from court decision text."""
    with logfire.span("case_citation"):
        filename_candidates = _filename_identifier_candidates(doc_ctx.file_name)
        if filename_candidates:
            return await _extract_filename_citation(doc_ctx, filename_candidates, jurisdiction)

        filename_candidate_text = ", ".join(filename_candidates) if filename_candidates else "[none detected]"
        instructions = (
            "Extract the canonical case citation as it appears in the court decision. "
            "Use the supplied beginning and end excerpts first because citations normally appear in document metadata. "
            "If those excerpts are inconclusive, use the navigation tools to inspect headings, metadata-like passages, "
            "and source-language terms for case numbers or citations. "
            "The original filename is secondary metadata. When the decision text has no citation, examine the filename "
            "carefully for a court or docket identifier before returning 'NA'. File-safe underscores, dashes, and spaces "
            "may encode the identifier's conventional separators and are not a reason to ignore it. If the filename "
            "clearly encodes an identifier, return its conventional form, copy the complete filename exactly into "
            "source_text, set source_location to 'original filename', and use medium or low confidence. "
            "Use the document's own citation format and language verbatim — do not translate, "
            "expand, or reformat court names, abbreviations, or docket numbers. Prefer the short canonical identifier "
            "over the full case header with parties, judges, and dates. Distinguish this decision's identifier from "
            "citations to authorities in its reasoning. "
            "For a positive result, source_text must be the exact verbatim line or compact passage containing the "
            "citation, source_location must identify the excerpt or numbered paragraph, and identifier_type must be a "
            "generic description of the identifier. "
            "If no citation is present in either the decision text or a clearly identifying filename, return 'NA' with "
            "low confidence — do not infer "
            "or fabricate — and return null for source_text, source_location, and identifier_type. "
            "Before returning 'NA', inspect the supplied excerpts and use at least one navigation tool to check the "
            "rest of the decision. "
            "The reasoning field must describe HOW the citation was located in the source "
            "without meta-commentary about the task, tools, or capabilities."
        )

        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": (
                    f"Jurisdiction: {jurisdiction}\n"
                    f"Legal System: {legal_system}\n\n"
                    f"Original filename: {doc_ctx.file_name or '[not available]'}\n\n"
                    f"Identifier-like filename segments: {filename_candidate_text}\n\n"
                    "The beginning and end of the court decision are supplied below. If the citation is not in these "
                    "excerpts, use the navigation tools to search the rest of the document before returning 'NA'.\n\n"
                    f"<court_decision_excerpts>\n{_citation_excerpts(doc_ctx.text)}\n</court_decision_excerpts>"
                ),
            },
        ]

        agent = Agent[DocumentContext](
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(
            agent,
            input=prompt,
            context=doc_ctx,
            validate=lambda output, tool_names: _validate_citation_against_document(doc_ctx, output, tool_names),
        )
