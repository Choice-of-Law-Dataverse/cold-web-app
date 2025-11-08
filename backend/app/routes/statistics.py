from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.auth import verify_jwt_token
from app.schemas.responses import JurisdictionCount
from app.services.statistics import StatisticsService

# Initialize service
statistics_service = StatisticsService()

# Define router
router = APIRouter(prefix="/statistics", tags=["Statistics"], dependencies=[Depends(verify_jwt_token)])


@router.get(
    "/count-by-jurisdiction",
    summary="Count records by jurisdiction for a specific table",
    description=(
        "Returns count of rows grouped by jurisdiction for the specified table. "
        "Supported tables: Court_Decisions, Domestic_Instruments, Literature."
    ),
    response_model=list[JurisdictionCount],
    responses={
        200: {
            "description": "Array of jurisdictions with their counts.",
            "content": {
                "application/json": {
                    "example": [
                        {"jurisdiction": "United Kingdom", "n": 97},
                        {"jurisdiction": "Australia", "n": 84},
                    ]
                }
            },
        },
        400: {"description": "Invalid table name provided."},
    },
)
def count_by_jurisdiction(
    request: Request,
    table: str = Query(..., description="Table name (e.g., 'Court_Decisions', 'Domestic_Instruments', 'Literature')"),
    limit: int | None = Query(None, ge=1, description="Optional limit on number of results to return"),
) -> list[JurisdictionCount]:
    """Returns count of rows grouped by jurisdiction for the specified table."""
    results = statistics_service.count_by_jurisdiction(table, limit)
    if not results and table not in ["Court_Decisions", "Domestic_Instruments", "Literature"]:
        raise HTTPException(status_code=400, detail=f"Invalid table name: {table}")
    return results
