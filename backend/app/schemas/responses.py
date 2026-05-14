from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.requests import FTSFilterOption
from app.schemas.search_result import AnySearchResult


class FullTextSearchResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    query: str | None = Field(default=None, description="The search query string that was submitted.")
    filters: list[FTSFilterOption] | None = Field(default=None, description="Active filters applied to the search.")
    total_matches: int = Field(..., description="Total number of matching records across all pages.")
    page: int = Field(..., description="Current page number (1-indexed).")
    page_size: int = Field(..., description="Number of results per page.")
    results: list[AnySearchResult] = Field(..., description="Array of search result records for the current page.")


class JurisdictionCoverage(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int = Field(..., description="Internal jurisdiction identifier.")
    name: str = Field(..., description="Full name of the jurisdiction (e.g. 'Switzerland').")
    cold_id: str | None = Field(default=None, description="CoLD identifier for the jurisdiction.")
    legal_family: str | None = Field(default=None, description="Legal tradition (e.g. 'Civil Law', 'Common Law').")
    irrelevant: bool | None = Field(default=None, description="Whether this jurisdiction is excluded from analysis.")
    answer_coverage: float = Field(0, description="Percentage of questionnaire items with substantive answers (0–100).")


class PendingSuggestionItem(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    created_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    moderation_status: str | None = None
    case_citation: str | None = None
    token_sub: str | None = None
    username: str | None = None
    user_email: str | None = None


class SuggestionDetailItem(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    created_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    moderation_status: str | None = None
    token_sub: str | None = None
    username: str | None = None
    user_email: str | None = None


class SitemapEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    loc: str = Field(..., description="Full URL of the page.")
    lastmod: str = Field(..., description="Last modification date in ISO 8601 format.")


class LandingPageJurisdiction(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str = Field(..., description="ISO 3166-1 Alpha-3 code (e.g. 'CHE').")
    has_data: int = Field(..., description="1 if the jurisdiction has substantive answer data, 0 otherwise.")


class ModerationSummaryItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    category: str = Field(..., description="URL-safe category slug (e.g. 'court-decisions').")
    label: str = Field(..., description="Human-readable category name (e.g. 'Court Decisions').")
    pending_count: int = Field(..., description="Number of suggestions awaiting moderation in this category.")


class StatusMessage(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: str = Field(..., description="Result status (e.g. 'success', 'ok').")
    message: str = Field(..., description="Human-readable description of the outcome.")


class JurisdictionCount(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "jurisdiction": "United Kingdom",
                    "n": 97,
                }
            ]
        },
    )

    jurisdiction: str = Field(..., description="Name of the jurisdiction")
    n: int = Field(..., ge=0, description="Count of records for this jurisdiction")


class SpecialistResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "createdAt": "2024-01-01T00:00:00",
                    "updatedAt": "2024-01-15T10:30:00",
                    "createdBy": "admin",
                    "updatedBy": "admin",
                    "ncOrder": 1.0,
                    "ncRecordId": "rec123",
                    "ncRecordHash": "hash123",
                    "specialist": "Dr. Jane Smith",
                    "created": "2024-01-01T00:00:00",
                }
            ]
        },
    )

    id: int = Field(..., description="Unique identifier for the specialist")
    created_at: datetime | None = Field(default=None, description="Timestamp when the record was created")
    updated_at: datetime | None = Field(default=None, description="Timestamp when the record was last updated")
    created_by: str | None = Field(default=None, description="User who created the record")
    updated_by: str | None = Field(default=None, description="User who last updated the record")
    nc_order: float | None = Field(default=None, description="NocoDB order field")
    nc_record_id: str | None = Field(default=None, description="NocoDB record identifier")
    nc_record_hash: str | None = Field(default=None, description="NocoDB record hash")
    specialist: str | None = Field(default=None, description="Name of the specialist")
    created: datetime | None = Field(default=None, description="Creation date from source data")
