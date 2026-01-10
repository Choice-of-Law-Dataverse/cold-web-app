"""Pydantic models for case analysis outputs."""

from typing import Literal

from pydantic import BaseModel, Field


class ColSectionOutput(BaseModel):
    """Output model for Choice of Law section extraction."""

    col_sections: list[str] = Field(description="List of extracted Choice of Law section texts")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of why these sections were extracted")

    def __str__(self) -> str:
        """Return all sections joined with double newlines."""
        return "\n\n".join(self.col_sections)


class CaseCitationOutput(BaseModel):
    """Output model for case citation extraction."""

    case_citation: str = Field(description="The case citation extracted from the text. Academic format preferred.")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the citation extraction")


class RelevantFactsOutput(BaseModel):
    """Output model for relevant facts extraction."""

    relevant_facts: str = Field(description="The relevant facts from the case")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the factual analysis")


class PILProvisionsOutput(BaseModel):
    """Output model for PIL provisions extraction."""

    pil_provisions: list[str] = Field(description="List of Private International Law provisions")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the provisions identified")


class ColIssueOutput(BaseModel):
    """Output model for Choice of Law issue identification."""

    col_issue: str = Field(description="The Choice of Law issue(s) in the case")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the identification: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the issue identification")


class CourtsPositionOutput(BaseModel):
    """Output model for court's position analysis."""

    courts_position: str = Field(description="The court's position on the CoL issue")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the analysis: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the court's reasoning")


class ObiterDictaOutput(BaseModel):
    """Output model for obiter dicta extraction."""

    obiter_dicta: str = Field(description="Obiter dicta from the court's opinion")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the obiter dicta identified")


class DissentingOpinionsOutput(BaseModel):
    """Output model for dissenting opinions extraction."""

    dissenting_opinions: str = Field(description="Dissenting opinions in the case")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the extraction: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of the dissenting opinion analysis")


class AbstractOutput(BaseModel):
    """Output model for case abstract."""

    abstract: str = Field(description="Concise abstract of the case")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level in the abstract quality: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(description="Explanation of how the abstract was constructed")
