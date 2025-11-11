from datetime import datetime

from pydantic import BaseModel, Field


class JurisdictionCount(BaseModel):
    """Response model for jurisdiction count statistics."""

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
    """Response model for a specialist record."""

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
