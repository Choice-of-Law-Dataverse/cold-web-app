from typing import Any, Dict, Optional, List
from datetime import date
from pydantic import BaseModel, Field, model_validator


class SuggestionPayload(BaseModel):
    # Accept any dict content as the "new data" suggestion from frontend
    data: Dict[str, Any] = Field(..., description="Arbitrary dictionary provided by the frontend as new data suggestion")
    source: Optional[str] = Field(None, description="Optional source/context identifier on the frontend")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {"table": "Answers", "id": "CHE_15-TC", "field": "Summary", "value": "Proposed correction"},
                    "source": "detail-view",
                }
            ]
        }
    }


class SuggestionResponse(BaseModel):
    id: int
    status: str = "stored"


# Typed suggestion schemas

class CourtDecisionSuggestion(BaseModel):
    # Required
    case_citation: str = Field(..., description="Case Citation")
    date_publication: date = Field(..., description="Date of Publication")
    official_source_url: str = Field(
        ..., description="Official Source (URL)"
    )
    official_source_pdf: Optional[str] = Field(
        None, description="Official Source (PDF link, storage key, or identifier)"
    )
    copyright_issues: str = Field(
        ..., description="Copyright issues (description or flag)"
    )

    # Optional
    original_text: Optional[str] = None
    english_translation: Optional[str] = None
    case_rank: Optional[str] = None
    jurisdiction: Optional[str] = None
    abstract: Optional[str] = None
    relevant_facts: Optional[str] = None
    pil_provisions: Optional[str] = None
    choice_of_law_issue: Optional[str] = None
    courts_position: Optional[str] = Field(
        None, description="Court's Position"
    )
    translated_excerpt: Optional[str] = None
    quote: Optional[str] = None
    decision_date: Optional[date] = Field(
        None, description="Decision date or other relevant date"
    )
    case_title: Optional[str] = None
    instance: Optional[str] = None
    official_keywords: Optional[str] = None
    publication_date_iso: Optional[str] = None

    @model_validator(mode="after")
    def _require_one_official_source(self):
        if not (self.official_source_url or self.official_source_pdf):
            raise ValueError("Either official_source_url or official_source_pdf is required")
        return self


class DomesticInstrumentSuggestion(BaseModel):
    # Required
    jurisdiction_link: str = Field(..., description="Jurisdiction Link")
    official_title: str = Field(
        ..., description="Official Title (e.g., Bundesgesetz über das IPR)"
    )
    title_en: str = Field(
        ..., description="Title in English (include jurisdiction demonym)"
    )
    entry_into_force: date = Field(..., description="Entry Into Force date")
    # Year of entry into force (automated)
    date_year_of_entry_into_force: Optional[int] = Field(
        None, description="Year of Entry Into Force (auto-derived from entry_into_force)"
    )

    # Required: either URL or PDF
    source_url: Optional[str] = Field(None, description="Source (URL)")
    source_pdf: Optional[str] = Field(
        None, description="Source (PDF link, storage key, or identifier)"
    )

    # Optional
    themes: Optional[List[str]] = None
    status: Optional[str] = None
    publication_date: Optional[date] = None
    abbreviation: Optional[str] = None
    compatible_hcch_principles: Optional[bool] = None
    compatible_uncitral_model_law: Optional[bool] = None

    @model_validator(mode="after")
    def _require_one_source(self):
        if not (self.source_url or self.source_pdf):
            raise ValueError("Either source_url or source_pdf is required")
        # auto-derive year if missing
        if self.entry_into_force and not self.date_year_of_entry_into_force:
            object.__setattr__(
                self, "date_year_of_entry_into_force", self.entry_into_force.year
            )
        return self


class RegionalInstrumentSuggestion(BaseModel):
    # Required
    abbreviation: str = Field(..., description="Abbreviation")

    # Optional
    title: Optional[str] = None
    url: Optional[str] = None
    attachment: Optional[str] = None
    instrument_date: Optional[date] = None


class InternationalInstrumentSuggestion(BaseModel):
    # Required
    name: str = Field(..., description="Name")
    url: str = Field(..., description="URL")
    attachment: str = Field(..., description="Attachment (link, storage key, or identifier)")
    instrument_date: date = Field(..., description="Date")


class LiteratureSuggestion(BaseModel):
    # All optional
    jurisdiction: Optional[str] = None
    publication_year: Optional[int] = None
    author: Optional[str] = None
    title: Optional[str] = None
    publication_title: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    publication_date: Optional[date] = None
    theme: Optional[str] = None
