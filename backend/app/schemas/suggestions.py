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
    date_publication: date = Field(..., description="Date [of Publication]")
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
    original_text: Optional[str] = Field(None, description="Original Text")
    english_translation: Optional[str] = Field(None, description="English Translation")
    case_rank: Optional[str] = Field(None, description="Case Rank")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    abstract: Optional[str] = Field(None, description="Abstract")
    relevant_facts: Optional[str] = Field(None, description="Relevant Facts")
    pil_provisions: Optional[str] = Field(None, description="PIL Provisions")
    choice_of_law_issue: Optional[str] = Field(None, description="Choice of Law Issue")
    courts_position: Optional[str] = Field(
        None, description="Court's Position"
    )
    translated_excerpt: Optional[str] = Field(None, description="Translated Excerpt")
    text_of_relevant_legal_provisions: Optional[str] = Field(None, description="Text of the Relevant Legal Provisions")
    quote: Optional[str] = None
    decision_date: Optional[date] = Field(
        None, description="Decision date or other relevant date"
    )
    case_title: Optional[str] = Field(None, description="Case Title")
    instance: Optional[str] = Field(None, description="Instance")
    official_keywords: Optional[str] = Field(None, description="Official Keywords")
    publication_date_iso: Optional[str] = Field(None, description="Publication Date ISO")

    @model_validator(mode="after")
    def _require_one_official_source(self):
        if not (self.official_source_url or self.official_source_pdf):
            raise ValueError("Either official_source_url or official_source_pdf is required")
        return self


class DomesticInstrumentSuggestion(BaseModel):
    # Required
    jurisdiction_link: str = Field(..., description="Jurisdiction Link")
    official_title: str = Field(
        ..., description="Official Title [e.g. Bundesgesetz über das Internationale Privatrecht/Loi sur le droit international privé]"
    )
    title_en: str = Field(
        ..., description="Title (in English) [include demonym before the title]"
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
    themes: Optional[List[str]] = Field(None, description="Themes")
    status: Optional[str] = Field(None, description="Status")
    publication_date: Optional[date] = Field(None, description="Publication Date")
    abbreviation: Optional[str] = Field(None, description="Abbrevation")
    compatible_hcch_principles: Optional[bool] = Field(None, description="Compatible With the HCCH Principles?")
    compatible_uncitral_model_law: Optional[bool] = Field(None, description="Compatible With the UNCITRAL Model Law?")

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
    title: Optional[str] = Field(None, description="Title")
    url: Optional[str] = Field(None, description="URL")
    attachment: Optional[str] = Field(None, description="Attachment")
    instrument_date: Optional[date] = Field(None, description="Date")


class InternationalInstrumentSuggestion(BaseModel):
    # Required
    name: str = Field(..., description="Name")
    url: str = Field(..., description="URL")
    attachment: str = Field(..., description="Attachment")
    instrument_date: date = Field(..., description="Date")


class LiteratureSuggestion(BaseModel):
    # All optional
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    publication_year: Optional[int] = Field(None, description="Publication Year")
    author: Optional[str] = Field(None, description="Author")
    title: Optional[str] = Field(None, description="Title")
    publication_title: Optional[str] = Field(None, description="Publication Title")
    isbn: Optional[str] = Field(None, description="ISBN")
    issn: Optional[str] = Field(None, description="ISSN")
    doi: Optional[str] = Field(None, description="DOI")
    url: Optional[str] = Field(None, description="Url")
    publication_date: Optional[date] = Field(None, description="Date")
    theme: Optional[str] = Field(None, description="Theme")


# New: Case Analyzer Suggestions (standalone; no direct DB merge)
class CaseAnalyzerSuggestion(BaseModel):
    # Meta
    username: Optional[str] = Field(None, description="Submitter Username")
    user_email: Optional[str] = Field(None, description="Submitter Email")
    model: Optional[str] = Field(None, description="Model used to analyze")

    # Core case fields
    case_citation: Optional[str] = Field(None, description="Case Citation")
    case_title: Optional[str] = Field(None, description="Case Title")
    court_name: Optional[str] = Field(None, description="Court Name")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    decision_date: Optional[date] = Field(None, description="Decision Date")
    source_url: Optional[str] = Field(None, description="Source URL")

    # Content
    is_common_law: Optional[bool] = Field(None, description="Common Law Jurisdiction")
    ratio_decidendi: Optional[str] = Field(None, description="Ratio Decidendi")
    obiter_dicta: Optional[str] = Field(None, description="Obiter Dicta")
    dissenting_opinions: Optional[str] = Field(None, description="Dissenting Opinions")
    courts_position: Optional[str] = Field(None, description="Court's Position (merged summary)")

    relevant_facts: Optional[str] = None
    legal_provisions: Optional[str] = Field(None, description="Relevant Legal Provisions")
    choice_of_law_issue: Optional[str] = None
    abstract: Optional[str] = None
    notes: Optional[str] = None

    # Raw material
    raw_data: Optional[str] = Field(None, description="Original analyzer output (for reference)")
