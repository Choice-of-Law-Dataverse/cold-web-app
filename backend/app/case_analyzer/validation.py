"""Evidence-aware semantic validation for case analyzer outputs."""

from collections.abc import Callable
from typing import Any

from .tools.document_nav import NAV_TOOLS
from .tools.models import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
)

type ValidatorFn = Callable[[Any, frozenset[str]], str | None]

NAV_TOOL_NAMES = frozenset(tool.name for tool in NAV_TOOLS)
EVIDENCE_TOOL_NAMES = NAV_TOOL_NAMES - {"list_headings"}
_PLACEHOLDERS = frozenset({"", "na", "n/a", "none", "not applicable", "unknown"})
_NEGATIVE_PHRASES = (
    "no dissent",
    "no minority opinion",
    "no obiter",
    "no relevant dissent",
    "no relevant obiter",
    "none identified",
    "not identified",
    "there is no dissent",
    "there is no obiter",
)


def has_navigation_evidence(tool_names: frozenset[str]) -> bool:
    """Return whether a content-bearing document-navigation tool was used."""
    return bool(tool_names & EVIDENCE_TOOL_NAMES)


def is_placeholder_text(value: str) -> bool:
    return value.strip().lower().rstrip(".") in _PLACEHOLDERS


def is_negative_text(value: str) -> bool:
    normalized = " ".join(value.strip().lower().split())
    return is_placeholder_text(normalized) or any(phrase in normalized for phrase in _NEGATIVE_PHRASES)


def is_meaningful_text(value: str, minimum_length: int) -> bool:
    stripped = value.strip()
    return len(stripped) >= minimum_length and not is_placeholder_text(stripped)


def _require_navigation_for_negative(label: str, tool_names: frozenset[str]) -> str | None:
    if has_navigation_evidence(tool_names):
        return None
    return (
        f"The negative {label} result was produced without inspecting the court decision. "
        "Use at least one document navigation tool to verify that the requested material is absent."
    )


def validate_col_section(output: ColSectionOutput, tool_names: frozenset[str]) -> str | None:
    if not has_navigation_evidence(tool_names):
        return "No court-decision content was inspected. Use the navigation tools before extracting Choice of Law sections."
    return validate_col_section_content(output, tool_names)


def validate_col_section_content(output: ColSectionOutput, _tool_names: frozenset[str]) -> str | None:
    """Validate persisted section content without requiring legacy tool metadata."""
    if not output.col_sections or any(not section.strip() for section in output.col_sections):
        return "No non-empty Choice of Law passages were returned. Re-read the decision and extract the relevant passages."
    return None


def validate_case_citation(output: CaseCitationOutput, tool_names: frozenset[str]) -> str | None:
    if not output.case_citation.strip():
        return "The case citation is empty. Re-examine the decision and return its citation or 'NA'."
    if is_placeholder_text(output.case_citation):
        if output.confidence != "low":
            return (
                "A missing case citation must have low confidence. Re-examine the document excerpts and original "
                "filename for an identifier before returning 'NA'."
            )
        navigation_error = _require_navigation_for_negative("case citation", tool_names)
        if navigation_error is not None:
            return navigation_error
        if output.source_text is not None or output.source_location is not None or output.identifier_type is not None:
            return (
                "You returned a negative case citation together with substantive citation evidence. Re-examine that "
                "evidence: if it identifies this decision, return the identifier as case_citation; otherwise return null "
                "source_text, source_location, and identifier_type."
            )
        return None
    if not output.source_text or not output.source_text.strip():
        return "The case citation has no verbatim source_text. Copy the exact line containing it from the decision."
    uses_filename_evidence = (
        output.source_location is not None and output.source_location.strip().casefold() == "original filename"
    )
    if output.case_citation not in output.source_text and not uses_filename_evidence:
        return "The case citation is not present verbatim in source_text. Copy both values exactly from the decision."
    if not output.source_location or not output.source_location.strip():
        return "The case citation has no source_location. Identify where its source_text was found."
    if not output.identifier_type or not output.identifier_type.strip():
        return "The case citation has no identifier_type. Describe the identifier using a generic category."
    return None


def validate_themes(output: ThemeClassificationOutput, tool_names: frozenset[str]) -> str | None:
    if not output.themes:
        return "No themes were returned. Classify at least one theme or return 'NA' after checking the decision."
    if output.themes == ["NA"]:
        return _require_navigation_for_negative("theme classification", tool_names)
    if "NA" in output.themes:
        return "'NA' cannot be combined with concrete themes. Return either concrete themes or only 'NA'."
    return None


def validate_pil_provisions(output: PILProvisionsOutput, tool_names: frozenset[str]) -> str | None:
    if any(not provision.strip() or is_placeholder_text(provision) for provision in output.pil_provisions):
        return "PIL provisions must contain only non-empty, actual authorities; remove placeholder entries."
    if not output.pil_provisions:
        return _require_navigation_for_negative("PIL provisions", tool_names)
    return None


def validate_relevant_facts(output: RelevantFactsOutput, _tool_names: frozenset[str]) -> str | None:
    if not is_meaningful_text(output.relevant_facts, 20):
        return "The relevant facts are empty, a placeholder, or too short. Provide a source-grounded factual narrative."
    return None


def validate_col_issue(output: ColIssueOutput, _tool_names: frozenset[str]) -> str | None:
    if not is_meaningful_text(output.col_issue, 20):
        return "The Choice of Law issue is empty, a placeholder, or too short. State the specific legal question."
    return None


def validate_courts_position(output: CourtsPositionOutput, _tool_names: frozenset[str]) -> str | None:
    if not is_meaningful_text(output.courts_position, 20):
        return "The court's position is empty, a placeholder, or too short. State its source-grounded position."
    return None


def validate_obiter_dicta(output: ObiterDictaOutput, tool_names: frozenset[str]) -> str | None:
    if not output.obiter_dicta.strip():
        return "The obiter dicta result is empty. Return the relevant observations or an explicit negative result."
    if is_negative_text(output.obiter_dicta):
        return _require_navigation_for_negative("obiter dicta", tool_names)
    if not is_meaningful_text(output.obiter_dicta, 20):
        return "The obiter dicta result is too short to be meaningful."
    return None


def validate_dissenting_opinions(output: DissentingOpinionsOutput, tool_names: frozenset[str]) -> str | None:
    if not output.dissenting_opinions.strip():
        return "The dissent result is empty. Return the relevant opinion or an explicit negative result."
    if is_negative_text(output.dissenting_opinions):
        return _require_navigation_for_negative("dissenting opinions", tool_names)
    if not is_meaningful_text(output.dissenting_opinions, 20):
        return "The dissent result is too short to be meaningful."
    return None


def validate_abstract(output: AbstractOutput, _tool_names: frozenset[str]) -> str | None:
    if not is_meaningful_text(output.abstract, 50):
        return "The abstract is empty, a placeholder, or too short. Synthesize a substantive case abstract."
    return None
