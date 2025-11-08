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
