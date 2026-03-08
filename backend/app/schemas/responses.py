from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.records import AnyRecord, RecordBase
from app.schemas.requests import FTSFilterOption


class FullTextSearchResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    query: str | None = None
    filters: list[FTSFilterOption] | None = None
    total_matches: int
    page: int
    page_size: int
    results: list[AnyRecord]


class CuratedDetailsRecord(RecordBase):
    cold_id: str | None = None
    hop1_relations: dict[str, list[dict[str, Any]] | None] | None = None


class JurisdictionCoverage(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    name: str
    alpha_3_code: str | None = None
    answer_coverage: float = 0
    irrelevant: bool | None = None
    jurisdiction_summary: str | None = None
    jurisdictional_differentiator: str | None = None
    legal_family: str | None = None
    type: str | None = None
    region: str | None = None


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

    loc: str
    lastmod: str


class LandingPageJurisdiction(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    has_data: int


class StatusMessage(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: str
    message: str


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
    created_at: datetime | None = Field(None, description="Timestamp when the record was created")
    updated_at: datetime | None = Field(None, description="Timestamp when the record was last updated")
    created_by: str | None = Field(None, description="User who created the record")
    updated_by: str | None = Field(None, description="User who last updated the record")
    nc_order: float | None = Field(None, description="NocoDB order field")
    nc_record_id: str | None = Field(None, description="NocoDB record identifier")
    nc_record_hash: str | None = Field(None, description="NocoDB record hash")
    specialist: str | None = Field(None, description="Name of the specialist")
    created: datetime | None = Field(None, description="Creation date from source data")
