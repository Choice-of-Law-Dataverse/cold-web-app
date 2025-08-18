from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


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
