from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class SuggestionPayload(BaseModel):
    # Accept any dict content as the "new data" suggestion from frontend
    data: dict[str, Any] = Field(
        ...,
        description="Arbitrary dictionary provided by the frontend as new data suggestion",
    )
    source: str | None = Field(None, description="Optional source/context identifier on the frontend")
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "table": "Answers",
                        "id": "CHE_15-TC",
                        "field": "Summary",
                        "value": "Proposed correction",
                    },
                    "source": "detail-view",
                    "submitter_email": "user@example.com",
                    "submitter_comments": "Found a typo in the field value.",
                }
            ]
        }
    }


class SuggestionResponse(BaseModel):
    id: int
    status: str = "stored"


# Typed suggestion schemas


class CourtDecisionSuggestion(BaseModel):
    # Edit mode: if set, this suggestion is an edit of an existing entity
    edit_entity_id: str | None = Field(None, description="ID of the existing entity being edited (None for new submissions)")

    # Required
    case_citation: str = Field(..., description="Case Citation")
    date_publication: date = Field(..., description="Date [of Publication]")
    official_source_url: str = Field(..., description="Official Source (URL)")
    copyright_issues: str = Field(..., description="Copyright issues (description or flag)")

    # Optional
    original_text: str | None = Field(None, description="Original Text")
    english_translation: str | None = Field(None, description="English Translation")
    case_rank: str | None = Field(None, description="Case Rank")
    jurisdiction: str | None = Field(None, description="Jurisdiction")
    abstract: str | None = Field(None, description="Abstract")
    relevant_facts: str | None = Field(None, description="Relevant Facts")
    pil_provisions: str | None = Field(None, description="PIL Provisions")
    choice_of_law_issue: str | None = Field(None, description="Choice of Law Issue")
    courts_position: str | None = Field(None, description="Court's Position")
    translated_excerpt: str | None = Field(None, description="Translated Excerpt")
    text_of_relevant_legal_provisions: str | None = Field(None, description="Text of the Relevant Legal Provisions")
    quote: str | None = None
    decision_date: date | None = Field(None, description="Decision date or other relevant date")
    case_title: str | None = Field(None, description="Case Title")
    instance: str | None = Field(None, description="Instance")
    official_keywords: str | None = Field(None, description="Official Keywords")
    publication_date_iso: str | None = Field(None, description="Publication Date ISO")

    # Submitter metadata
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "case_citation": "Doe v. Smith, 123 A.3d 456",
                "date_publication": "2024-05-01",
                "official_source_url": "https://example.org/cases/123",
                "copyright_issues": "none",
                "jurisdiction": "AR",
                "case_title": "Doe v. Smith",
                "submitter_email": "user@example.com",
                "submitter_comments": "Spotted a typo in the abstract.",
            }
        }
    }

    @model_validator(mode="after")
    def _require_one_official_source(self):
        if not self.official_source_url:
            raise ValueError("official_source_url is required")
        return self


class DomesticInstrumentSuggestion(BaseModel):
    # Edit mode: if set, this suggestion is an edit of an existing entity
    edit_entity_id: str | None = Field(None, description="ID of the existing entity being edited (None for new submissions)")

    # Required
    jurisdiction_link: str = Field(..., description="Jurisdiction Link")
    official_title: str = Field(
        ...,
        description="Official Title [e.g. Bundesgesetz über das Internationale Privatrecht/Loi sur le droit international privé]",  # noqa: E501
    )
    title_en: str = Field(..., description="Title (in English) [include demonym before the title]")
    entry_into_force: date = Field(..., description="Entry Into Force date")
    # Year of entry into force (automated)
    date_year_of_entry_into_force: int | None = Field(
        None,
        description="Year of Entry Into Force (auto-derived from entry_into_force)",
    )

    # Required: Source URL
    source_url: str | None = Field(None, description="Source (URL)")

    # Optional
    themes: list[str] | None = Field(None, description="Themes")
    status: str | None = Field(None, description="Status")
    publication_date: date | None = Field(None, description="Publication Date")
    abbreviation: str | None = Field(None, description="Abbrevation")
    compatible_hcch_principles: bool | None = Field(None, description="Compatible With the HCCH Principles?")
    compatible_uncitral_model_law: bool | None = Field(None, description="Compatible With the UNCITRAL Model Law?")

    # Submitter metadata
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "jurisdiction_link": "https://example.org/jurisdictions/ar",
                "official_title": "Ley de Derecho Internacional Privado",
                "title_en": "Argentinian Private International Law Act",
                "entry_into_force": "2023-01-01",
                "source_url": "https://boletin.oficial.ar/ley.pdf",
                "themes": ["contract", "choice-of-law"],
                "submitter_email": "user@example.com",
                "submitter_comments": "Newer consolidated version available.",
            }
        }
    }

    @model_validator(mode="after")
    def _require_one_source(self):
        if not self.source_url:
            raise ValueError("source_url is required")
        # auto-derive year if missing
        if self.entry_into_force and not self.date_year_of_entry_into_force:
            object.__setattr__(self, "date_year_of_entry_into_force", self.entry_into_force.year)
        return self


class RegionalInstrumentSuggestion(BaseModel):
    # Edit mode: if set, this suggestion is an edit of an existing entity
    edit_entity_id: str | None = Field(None, description="ID of the existing entity being edited (None for new submissions)")

    # Required
    abbreviation: str = Field(..., description="Abbreviation")

    # Optional
    title: str | None = Field(None, description="Title")
    url: str | None = Field(None, description="URL")
    instrument_date: date | None = Field(None, description="Date")

    # Submitter metadata
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "abbreviation": "EU-Rome I",
                "title": "Regulation (EC) No 593/2008 (Rome I)",
                "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32008R0593",
                "instrument_date": "2008-06-17",
                "submitter_email": "user@example.com",
                "submitter_comments": "Add link to consolidated version.",
            }
        }
    }


class InternationalInstrumentSuggestion(BaseModel):
    # Edit mode: if set, this suggestion is an edit of an existing entity
    edit_entity_id: str | None = Field(None, description="ID of the existing entity being edited (None for new submissions)")

    # Required
    name: str = Field(..., description="Name")
    url: str = Field(..., description="URL")
    instrument_date: date = Field(..., description="Date")

    # Submitter metadata
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "HCCH Principles on Choice of Law in International Commercial Contracts",
                "url": "https://www.hcch.net/en/instruments/conventions/full-text/?cid=135",
                "instrument_date": "2015-03-19",
                "submitter_email": "user@example.com",
                "submitter_comments": "Typo in the title capitalization.",
            }
        }
    }


class LiteratureSuggestion(BaseModel):
    # Edit mode: if set, this suggestion is an edit of an existing entity
    edit_entity_id: str | None = Field(None, description="ID of the existing entity being edited (None for new submissions)")

    # All optional
    jurisdiction: str | None = Field(None, description="Jurisdiction")
    publication_year: int | None = Field(None, description="Publication Year")
    author: str | None = Field(None, description="Author")
    title: str | None = Field(None, description="Title")
    publication_title: str | None = Field(None, description="Publication Title")
    isbn: str | None = Field(None, description="ISBN")
    issn: str | None = Field(None, description="ISSN")
    doi: str | None = Field(None, description="DOI")
    url: str | None = Field(None, description="Url")
    publication_date: date | None = Field(None, description="Date")
    theme: str | None = Field(None, description="Theme")

    # Submitter metadata
    submitter_email: EmailStr | None = Field(None, description="Submitter e-mail address")
    submitter_comments: str | None = Field(None, description="Submitter comments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "author": "Jane Doe",
                "title": "Choice of Law in Cross-Border Contracts",
                "publication_year": 2022,
                "doi": "10.1000/j.jicl.2022.12345",
                "url": "https://doi.org/10.1000/j.jicl.2022.12345",
                "submitter_email": "user@example.com",
                "submitter_comments": "Add missing ISSN.",
            }
        }
    }


# New: Case Analyzer Suggestions (standalone; no direct DB merge)
class CaseAnalyzerSuggestion(BaseModel):
    # Meta
    draft_id: int | None = Field(None, description="Draft ID to merge with")
    username: str | None = Field(None, description="Submitter Username")
    user_email: str | None = Field(None, description="Submitter Email")
    model: str | None = Field(None, description="Model used to analyze")

    # Core case fields
    case_citation: str | None = Field(None, description="Case Citation")
    case_title: str | None = Field(None, description="Case Title")
    court_name: str | None = Field(None, description="Court Name")
    jurisdiction: str | None = Field(None, description="Jurisdiction")
    decision_date: date | None = Field(None, description="Decision Date")
    source_url: str | None = Field(None, description="Source URL")

    # Content
    is_common_law: bool | None = Field(None, description="Common Law Jurisdiction")
    ratio_decidendi: str | None = Field(None, description="Ratio Decidendi")
    obiter_dicta: str | None = Field(None, description="Obiter Dicta")
    dissenting_opinions: str | None = Field(None, description="Dissenting Opinions")
    courts_position: str | None = Field(None, description="Court's Position (merged summary)")

    relevant_facts: str | None = None
    legal_provisions: str | None = Field(None, description="Relevant Legal Provisions")
    choice_of_law_issue: str | None = None
    abstract: str | None = None
    notes: str | None = None

    # Raw material
    raw_data: str | None = Field(None, description="Original analyzer output (for reference)")
