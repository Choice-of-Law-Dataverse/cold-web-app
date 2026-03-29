"""Pydantic models for case analyzer outputs and classification."""

import re
from dataclasses import dataclass
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

_REPETITION_RE = re.compile(r"(.{5,80}?)\1{3,}\s*$")


def _strip_repetitive_suffix(text: str) -> str:
    """Remove trailing repetitive garbage from LLM output (e.g. 'PMID: N/A.' looped)."""
    return _REPETITION_RE.sub("", text).rstrip()


@dataclass
class StepResult[T]:
    output: T
    response_id: str | None = None


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
        """Return all sections joined with double newlines."""
        return "\n\n".join(self.col_sections)


class CaseCitationOutput(ConfidenceReasoningModel):
    case_citation: str = Field(description="The case citation extracted from the text. Academic format preferred.")


class RelevantFactsOutput(ConfidenceReasoningModel):
    relevant_facts: str = Field(description="The relevant facts from the case")


class PILProvisionsOutput(ConfidenceReasoningModel):
    pil_provisions: list[str] = Field(description="List of Private International Law provisions")


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


AnalysisStep = Literal[
    "theme_classification",
    "relevant_facts",
    "pil_provisions",
    "col_issue",
    "courts_position",
    "obiter_dicta",
    "dissenting_opinions",
]


class ConsistencyIssue(BaseModel):
    step: AnalysisStep = Field(description="The analysis step that has an inconsistency")
    description: str = Field(description="What is inconsistent and why")
    severity: Literal["low", "medium", "high"] = Field(description="How severe the inconsistency is")


class ConsistencyCheckOutput(BaseModel):
    is_consistent: bool = Field(description="Whether the analysis outputs are internally consistent")
    issues: list[ConsistencyIssue] = Field(default_factory=list, description="List of inconsistencies found")


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
