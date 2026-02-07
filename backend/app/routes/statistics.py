from fastapi import APIRouter, Depends, Query

from app.auth import verify_frontend_request
from app.schemas.responses import JurisdictionCount
from app.services.statistics import StatisticsService


def get_statistics_service() -> StatisticsService:
    """Dependency function to lazily instantiate the StatisticsService."""
    return StatisticsService()


# Define router
router = APIRouter(prefix="/statistics", tags=["Statistics"], dependencies=[Depends(verify_frontend_request)])


@router.get(
    "/jurisdictions-with-answer-percentage",
    summary="Get all jurisdictions with answer data percentage",
    description=(
        "Returns all jurisdictions with their complete data plus the percentage of answers "
        "that contain data (not 'no data'). Percentage is calculated per jurisdiction."
    ),
    responses={
        200: {
            "description": "Array of jurisdictions with all fields plus answer_coverage.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "Name": "United Kingdom",
                            "Alpha_3_Code": "GBR",
                            "Legal_Family": "Common Law",
                            "Answer_Coverage": 67.33,
                        },
                        {
                            "id": 2,
                            "Name": "Australia",
                            "Alpha_3_Code": "AUS",
                            "Legal_Family": "Common Law",
                            "Answer_Coverage": 85.5,
                        },
                    ]
                }
            },
        },
    },
)
def get_jurisdictions_with_answer_coverage(
    statistics_service: StatisticsService = Depends(get_statistics_service),
):
    """Returns all jurisdictions with percentage of answers containing data."""

    return statistics_service.get_jurisdictions_with_answer_coverage()


@router.get(
    "/count-by-jurisdiction",
    summary="Count records by jurisdiction for a specific table",
    description=(
        "Returns count of rows grouped by jurisdiction for the specified table. "
        "Supported tables: Court Decisions, Domestic Instruments, Literature."
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
    table: str = Query(..., description="Table name (e.g., 'Court Decisions', 'Domestic Instruments', 'Literature')"),
    limit: int | None = Query(None, ge=1, description="Optional limit on number of results to return"),
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> list[JurisdictionCount]:
    """Returns count of rows grouped by jurisdiction for the specified table."""

    return statistics_service.count_by_jurisdiction(table, limit)
