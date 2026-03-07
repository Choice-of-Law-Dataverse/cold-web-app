from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.records import RecordBase


class FullTextSearchResponse(BaseModel):
    test: bool
    total_matches: int
    page: int
    page_size: int
    results: list[RecordBase]


class CuratedDetailsRecord(RecordBase):
    cold_id: str | None = None
    hop1_relations: dict[str, list[dict[str, str | None]]] | None = None


class JurisdictionCoverage(BaseModel):
    id: int
    Name: str

    model_config = {"extra": "allow"}


class PendingSuggestionItem(BaseModel):
    id: int
    created_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None

    model_config = {"extra": "allow"}


class SuggestionDetailItem(BaseModel):
    id: int
    created_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    moderation_status: str | None = None

    model_config = {"extra": "allow"}


class SitemapEntry(BaseModel):
    loc: str
    lastmod: str


class LandingPageJurisdiction(BaseModel):
    code: str
    has_data: int


class StatusMessage(BaseModel):
    status: str
    message: str


class JurisdictionCount(BaseModel):
    jurisdiction: str = Field(..., description="Name of the jurisdiction")
    n: int = Field(..., ge=0, description="Count of records for this jurisdiction")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "jurisdiction": "United Kingdom",
                    "n": 97,
                }
            ]
        }
    }


class SpecialistResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the specialist")
    created_at: datetime | None = Field(None, description="Timestamp when the record was created")
    updated_at: datetime | None = Field(None, description="Timestamp when the record was last updated")
    created_by: str | None = Field(None, description="User who created the record")
    updated_by: str | None = Field(None, description="User who last updated the record")
    nc_order: float | None = Field(None, description="NocoDB order field")
    ncRecordId: str | None = Field(None, description="NocoDB record identifier")
    ncRecordHash: str | None = Field(None, description="NocoDB record hash")
    Specialist: str | None = Field(None, description="Name of the specialist")
    Created: datetime | None = Field(None, description="Creation date from source data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-15T10:30:00",
                    "created_by": "admin",
                    "updated_by": "admin",
                    "nc_order": 1.0,
                    "ncRecordId": "rec123",
                    "ncRecordHash": "hash123",
                    "Specialist": "Dr. Jane Smith",
                    "Created": "2024-01-01T00:00:00",
                }
            ]
        }
    }
