import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic.alias_generators import to_camel

from app.auth import verify_frontend_request
from app.schemas.details import TABLE_DETAIL_MODELS, AnyDetail, DetailBase
from app.schemas.records import AnyRecord, validate_record
from app.schemas.requests import (
    CuratedDetailsRequest,
    FullTableRequest,
    FullTextSearchRequest,
)
from app.schemas.responses import FullTextSearchResponse, SpecialistResponse
from app.schemas.search_result import validate_search_result
from app.services.search import SearchService


def _normalize_to_camel(key: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return to_camel(s.lower().rstrip("_"))


def _camel_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {_normalize_to_camel(k): _camel_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_camel_keys(item) for item in obj]
    return obj


def get_search_service() -> SearchService:
    """Dependency function to lazily instantiate the SearchService."""
    return SearchService()


router = APIRouter(
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(verify_frontend_request)],
)


@router.post(
    "/",
    summary="Full-text search across CoLD data",
    description=(
        "Searches across multiple domains (Answers, HCCH Answers, Court Decisions, Domestic Instruments, Regional Instruments, International Instruments, Literature, Arbitral Awards, and Arbitral Rules). "  # noqa: E501
        "Filters support user-facing fields like 'tables', 'Jurisdictions', or 'Themes'. "
        "You can sort by date and paginate results."
    ),
    responses={
        200: {
            "description": "Search results including pagination and total matches.",
            "content": {
                "application/json": {
                    "example": {
                        "query": "example search",
                        "filters": [{"column": "tables", "values": ["Answers"]}],
                        "total_matches": 2,
                        "page": 1,
                        "page_size": 2,
                        "results": [
                            {
                                "source_table": "Answers",
                                "id": "CHE_15-TC",
                                "Title": "…",
                            },
                            {
                                "source_table": "Court Decisions",
                                "id": "CD-GBR-1167",
                                "Title": "…",
                            },
                        ],
                    }
                }
            },
        }
    },
)
def handle_full_text_search(
    body: FullTextSearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> FullTextSearchResponse:
    search_string = body.search_string
    filters = body.filters or []
    page = body.page
    page_size = body.page_size
    sort_by_date = body.sort_by_date or False
    response_type = body.response_type or "parsed"
    if response_type != "parsed":
        raise HTTPException(
            status_code=400,
            detail="Only response_type='parsed' is supported for typed search results",
        )

    raw = search_service.full_text_search(
        search_string,
        filters,
        page,
        page_size,
        sort_by_date,
        response_type="parsed",
    )
    validated_results = [validate_search_result(r) for r in raw.pop("results", [])]
    return FullTextSearchResponse(results=validated_results, **raw)


@router.post(
    "/details",
    summary="Fetch a curated record by CoLD ID including relations",
    description="Given a table and a CoLD ID, returns the record with all first-hop relations in a standardized shape.",
    response_model=AnyDetail,
    responses={404: {"description": "Record not found."}},
)
def handle_entity_detail(
    body: CuratedDetailsRequest,
    search_service: SearchService = Depends(get_search_service),
) -> AnyDetail:
    try:
        result = search_service.get_entity_detail(body.table, body.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not result:
        raise HTTPException(status_code=404, detail=f"No record found for {body.id} in {body.table}")
    model = TABLE_DETAIL_MODELS.get(result.get("source_table", ""), DetailBase)
    return model.model_validate(result)


@router.post(
    "/full_table",
    summary="Return full or filtered table",
    description=(
        "Returns all records from the specified table or a filtered subset. Filters accept user-facing field names and values (mapping-aware)."  # noqa: E501
    ),
    responses={
        200: {
            "description": "Array of transformed records from the requested table.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "source_table": "Answers",
                            "id": "CHE_15-TC",
                            "Jurisdictions": ["Switzerland"],
                            "Title": "…",
                        }
                    ]
                }
            },
        },
        400: {"description": "Missing or invalid table parameter."},
        500: {"description": "Server error while querying the table."},
    },
)
def return_full_table(
    body: FullTableRequest,
    search_service: SearchService = Depends(get_search_service),
) -> list[AnyRecord]:
    table = body.table
    filters = body.filters or []
    response_type = getattr(body, "response_type", "parsed")

    if not table:
        raise HTTPException(status_code=400, detail="No table provided")

    try:
        if filters:
            results = search_service.filtered_table(table, filters, response_type=response_type)
        else:
            results = search_service.full_table(table, response_type=response_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return [validate_record(_camel_keys(r)) for r in results]


@router.get(
    "/specialists/{jurisdiction_alpha_code}",
    response_model=list[SpecialistResponse],
    summary="Get specialists by jurisdiction",
    description="Returns all specialists associated with a specific jurisdiction using Alpha_3_Code.",
    responses={
        200: {
            "description": "Array of specialists for the given jurisdiction.",
            "content": {
                "application/json": {
                    "example": [
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
            },
        },
        404: {"description": "Jurisdiction not found."},
        500: {"description": "Server error while querying specialists."},
    },
)
def get_specialists_by_jurisdiction(
    jurisdiction_alpha_code: str,
    search_service: SearchService = Depends(get_search_service),
) -> list[SpecialistResponse]:
    try:
        results = search_service.get_specialists_by_jurisdiction(jurisdiction_alpha_code)
        return [SpecialistResponse(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
