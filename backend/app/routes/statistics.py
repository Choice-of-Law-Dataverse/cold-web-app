from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.responses import JurisdictionCount, JurisdictionCoverage
from app.services.entity_list import EntityListService
from app.services.statistics import StatisticsService


def get_statistics_service() -> StatisticsService:
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
    summary="Jurisdiction answer coverage percentages",
    description=(
        "Returns every jurisdiction with its metadata (name, Alpha-3 code, legal family) and "
        "an `answer_coverage` percentage indicating how many of the standardised questionnaire "
        "questions have substantive answers (i.e. not 'No data'). Useful for assessing "
        "data completeness across jurisdictions."
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
    summary="Record counts grouped by jurisdiction for a table",
    description=(
        "Returns the number of records per jurisdiction for the given table. "
        "Supported tables: **Court Decisions**, **Domestic Instruments**, **Literature**. "
        "Useful for visualising geographic distribution of data (e.g. choropleth maps)."
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
    return statistics_service.count_by_jurisdiction(table, limit)


@router.get(
    "/counts",
    summary="Record counts per entity type",
    description=(
        "Returns the total number of records for each entity type in the dataverse "
        "(Court Decisions, Domestic Instruments, Literature, etc.). "
        "Pass an optional `jurisdiction` Alpha-3 code to scope counts to a single country. "
        "Useful for dashboard summaries and data completeness overviews."
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
