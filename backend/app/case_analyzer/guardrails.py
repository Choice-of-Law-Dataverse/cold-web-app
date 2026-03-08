"""Output validation functions for case analyzer steps.

Each validator returns None if valid, or an error message string to use as a retry prompt.
"""

from typing import get_args

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
    Theme,
    ThemeClassificationOutput,
)

VALID_THEMES: set[str] = set(get_args(Theme)) | {"NA"}

MIN_TEXT_LENGTH = 20


def validate_col_section(output: ColSectionOutput) -> str | None:
    if not output.col_sections or all(not s.strip() for s in output.col_sections):
        return (
            "Your previous response returned empty Choice of Law sections. "
            "Re-read the court decision and extract the relevant passages dealing with choice of law."
        )
    return None


def validate_themes(output: ThemeClassificationOutput) -> str | None:
    invalid = [t for t in output.themes if t not in VALID_THEMES]
    if invalid:
        return (
            f"Your previous response contained invalid themes: {invalid}. "
            f"Only use themes from this list: {sorted(VALID_THEMES)}."
        )
    if not output.themes:
        return (
            "Your previous response returned no themes. "
            "Re-analyze the court decision and classify at least one PIL theme, or 'NA' if none apply."
        )
    return None


def validate_case_citation(output: CaseCitationOutput) -> str | None:
    if not output.case_citation or len(output.case_citation.strip()) < 5:
        return (
            "Your previous response returned an empty or too-short case citation. "
            "Re-examine the court decision and extract the full academic citation."
        )
    return None


def validate_relevant_facts(output: RelevantFactsOutput) -> str | None:
    if not output.relevant_facts or len(output.relevant_facts.strip()) < MIN_TEXT_LENGTH:
        return (
            "Your previous response returned empty or insufficient relevant facts. "
            "Re-read the court decision and extract the key facts relevant to the choice of law analysis."
        )
    return None


def validate_pil_provisions(output: PILProvisionsOutput) -> str | None:
    if not output.pil_provisions or all(not p.strip() for p in output.pil_provisions):
        return (
            "Your previous response returned no PIL provisions. "
            "Re-examine the court decision and extract all referenced Private International Law provisions."
        )
    return None


def validate_col_issue(output: ColIssueOutput) -> str | None:
    if not output.col_issue or len(output.col_issue.strip()) < MIN_TEXT_LENGTH:
        return (
            "Your previous response returned an empty or too-short Choice of Law issue. "
            "Re-analyze the court decision and clearly articulate the choice of law issue."
        )
    return None


def validate_courts_position(output: CourtsPositionOutput) -> str | None:
    if not output.courts_position or len(output.courts_position.strip()) < MIN_TEXT_LENGTH:
        return (
            "Your previous response returned an empty or too-short court's position. "
            "Re-examine the court decision and describe the court's reasoning and conclusion on the choice of law issue."
        )
    return None


def validate_obiter_dicta(output: ObiterDictaOutput) -> str | None:
    if not output.obiter_dicta or len(output.obiter_dicta.strip()) < MIN_TEXT_LENGTH:
        return (
            "Your previous response returned empty obiter dicta. "
            "Re-read the court decision and extract any obiter dicta remarks relevant to choice of law."
        )
    return None


def validate_dissenting_opinions(output: DissentingOpinionsOutput) -> str | None:
    if not output.dissenting_opinions or len(output.dissenting_opinions.strip()) < MIN_TEXT_LENGTH:
        return (
            "Your previous response returned empty dissenting opinions. "
            "Re-examine the court decision for any dissenting or minority opinions on choice of law."
        )
    return None


def validate_abstract(output: AbstractOutput) -> str | None:
    if not output.abstract or len(output.abstract.strip()) < 50:
        return (
            "Your previous response returned an empty or too-short abstract. "
            "Synthesize all the analysis results into a comprehensive abstract of the case."
        )
    return None
