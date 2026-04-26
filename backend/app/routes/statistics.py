from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.responses import JurisdictionCount, JurisdictionCoverage
from app.services.entity_list import EntityListService
from app.services.statistics import StatisticsService


def get_statistics_service() -> StatisticsService:
    """Dependency function to lazily instantiate the StatisticsService."""
    return StatisticsService()


def get_entity_list_service() -> EntityListService:
    return EntityListService()


class EntityCountsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    counts: dict[str, int]
    jurisdiction: str | None = None


router = APIRouter(prefix="/statistics", tags=["Statistics"])


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
) -> list[JurisdictionCoverage]:
    results = statistics_service.get_jurisdictions_with_answer_coverage()
    return [JurisdictionCoverage(**r) for r in results]


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


@router.get(
    "/counts",
    summary="Counts for every entity in the dataverse",
    description=(
        "Returns counts per entity type, optionally scoped to a jurisdiction. "
        "Plain GET so it can be cached at the edge by Cloudflare."
    ),
    response_model=EntityCountsResponse,
)
def get_entity_counts(
    jurisdiction: Annotated[
        str | None,
        Query(description="Optional Alpha-3 code; only counts entities tagged to it."),
    ] = None,
    service: EntityListService = Depends(get_entity_list_service),
) -> EntityCountsResponse:
    try:
        counts = service.count_all(jurisdiction)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to compute counts") from exc

    return EntityCountsResponse(counts=counts, jurisdiction=jurisdiction)
