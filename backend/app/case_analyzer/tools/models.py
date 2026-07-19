"""Pydantic models for case analyzer outputs and classification."""

import re
from dataclasses import dataclass, field
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

_REPETITION_RE = re.compile(r"(.{5,80}?)\1{3,}\s*$")


def _strip_repetitive_suffix(text: str) -> str:
    return _REPETITION_RE.sub("", text).rstrip()


@dataclass
class StepResult[T]:
    output: T
    response_id: str | None = None
    tool_names: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)


class ConfidenceReasoningModel(BaseModel):
    """Shared confidence and reasoning fields."""

    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the analysis: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation supporting the analysis")

    @model_validator(mode="after")
    def _sanitize_strings(self) -> Self:
        for name in self.__class__.model_fields:
            value = getattr(self, name)
            if isinstance(value, str):
                setattr(self, name, _strip_repetitive_suffix(value))
            elif isinstance(value, list):
                setattr(self, name, [_strip_repetitive_suffix(v) if isinstance(v, str) else v for v in value])
        return self


class ColSectionOutput(ConfidenceReasoningModel):
    col_sections: list[str] = Field(description="List of extracted Choice of Law section texts")

    def __str__(self) -> str:
        return "\n\n".join(self.col_sections)


class ColRetrievalQueryPlan(BaseModel):
    queries: list[str] = Field(
        description=(
            "Two to six short case-specific search queries in the judgment's source language(s), using terms likely "
            "to locate the court's choice-of-law reasoning and holding"
        )
    )


ColCandidateRole = Literal[
    "court_holding",
    "court_reasoning",
    "party_argument",
    "cited_authority",
    "procedural_context",
]


class ColCandidateDecision(BaseModel):
    candidate_id: str = Field(description="The candidate identifier exactly as provided")
    disposition: Literal["include", "exclude", "needs_additional_context"]
    reason: str = Field(description="Concise source-grounded reason for the disposition")
    role: ColCandidateRole | None = Field(
        default=None,
        description="Required for included candidates; null for excluded candidates",
    )
    selected_paragraphs: list[int] = Field(
        default_factory=list,
        description=(
            "For included candidates, the exact numbered source paragraphs to reproduce; empty for excluded candidates"
        ),
    )


class ColCandidateAuditOutput(ConfidenceReasoningModel):
    decisions: list[ColCandidateDecision] = Field(description="Exactly one disposition for every supplied retrieval candidate")


class CaseCitationOutput(ConfidenceReasoningModel):
    case_citation: str = Field(
        description=(
            "Highest-priority canonical identifier exactly as it appears in the decision: prefer an official neutral "
            "identifier such as ECLI, then an official reporter citation, then a docket or case number. Never return a "
            "descriptive page title, court name, decision date, publication status, or party caption. Use the document's "
            "own format and language; do not translate or expand abbreviations. If only the original filename "
            "unambiguously encodes an identifier, file-safe separators may be normalized into its conventional form. "
            "Return 'NA' when neither source provides a citation."
        )
    )
    source_text: str | None = Field(
        description=(
            "Exact verbatim line or compact passage from the decision containing the case citation, or the complete "
            "original filename when that is the only source. Return null when case_citation is 'NA'."
        )
    )
    source_location: str | None = Field(
        description=(
            "Location of source_text: 'document beginning', 'document end', 'original filename', or a numbered paragraph "
            "returned by a navigation tool. Return null when case_citation is 'NA'."
        )
    )
    identifier_type: str | None = Field(
        description=(
            "Short generic description of the identifier, such as neutral citation, docket number, reporter citation, "
            "or ECLI. Return null when case_citation is 'NA'."
        )
    )

    @model_validator(mode="after")
    def _normalize_negative_evidence(self) -> Self:
        placeholders = {"", "na", "n/a", "none", "not applicable", "unknown"}

        def is_placeholder(value: str | None) -> bool:
            return value is None or value.strip().lower().rstrip(".") in placeholders

        if is_placeholder(self.case_citation):
            if is_placeholder(self.source_text):
                self.source_text = None
            if is_placeholder(self.source_location):
                self.source_location = None
            if is_placeholder(self.identifier_type):
                self.identifier_type = None
        return self


class RelevantFactsOutput(ConfidenceReasoningModel):
    relevant_facts: str = Field(description="The relevant facts from the case")


class PILProvisionsOutput(ConfidenceReasoningModel):
    pil_provisions: list[str] = Field(
        description=(
            "List of Private International Law provisions cited in the decision. "
            "Each list item must be an actual provision; never include 'NA' or other "
            "placeholder strings. Return an empty list if none are cited."
        )
    )


class ColIssueOutput(ConfidenceReasoningModel):
    col_issue: str = Field(description="The Choice of Law issue(s) in the case")


class CourtsPositionOutput(ConfidenceReasoningModel):
    courts_position: str = Field(description="The court's position on the CoL issue")


class ObiterDictaOutput(ConfidenceReasoningModel):
    obiter_dicta: str = Field(description="Obiter dicta from the court's opinion")


class DissentingOpinionsOutput(ConfidenceReasoningModel):
    dissenting_opinions: str = Field(description="Dissenting opinions in the case")


class AbstractOutput(ConfidenceReasoningModel):
    abstract: str = Field(description="Concise abstract of the case")


Theme = Literal[
    "Party autonomy",
    "Tacit choice",
    "Partial choice",
    "Absence of choice",
    "Arbitration",
    "Freedom of Choice",
    "Rules of Law",
    "Dépeçage",
    "Public policy",
    "Mandatory rules",
    "Consumer contracts",
    "Employment contracts",
]

ThemeWithNA = Theme | Literal["NA"]


class JurisdictionOutput(ConfidenceReasoningModel):
    legal_system_type: str = Field(
        description="The type of legal system (e.g., 'Civil-law jurisdiction', 'Common-law jurisdiction', 'Indian jurisdiction')"
    )
    precise_jurisdiction: str = Field(description="The specific jurisdiction (e.g., 'Switzerland', 'United States', 'India')")
    jurisdiction_code: str = Field(description="ISO country code for the jurisdiction (e.g., 'CH', 'US', 'IN')")


class ThemeClassificationOutput(ConfidenceReasoningModel):
    themes: list[ThemeWithNA] = Field(description="List of classified PIL themes")

    @model_validator(mode="after")
    def _dedupe_themes(self) -> Self:
        seen: set[str] = set()
        deduped: list[ThemeWithNA] = []
        for theme in self.themes:
            if theme not in seen:
                seen.add(theme)
                deduped.append(theme)
        self.themes = deduped
        return self
