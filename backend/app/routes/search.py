from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_frontend_request
from app.schemas.requests import (
    CuratedDetailsRequest,
    FullTableRequest,
    FullTextSearchRequest,
)
from app.schemas.responses import SpecialistResponse
from app.services.search import SearchService

search_service = SearchService()

router = APIRouter(
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(verify_frontend_request)],
)


@router.post(
    "/",
    summary="Full-text search across CoLD data",
    description=(
        "Searches across multiple domains (Answers, HCCH Answers, Court Decisions, Domestic Instruments, Regional Instruments, International Instruments, and Literature). "  # noqa: E501
        "Filters support user-facing fields like 'tables', 'Jurisdictions', or 'Themes'. "
        "You can sort by date and paginate results."
    ),
    responses={
        200: {
            "description": "Search results including pagination and total matches.",
            "content": {
                "application/json": {
                    "example": {
                        "test": False,
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
def handle_full_text_search(body: FullTextSearchRequest):
    search_string = body.search_string
    filters = body.filters or []
    page = body.page
    page_size = body.page_size
    sort_by_date = getattr(body, "sort_by_date", False)
    response_type = getattr(body, "response_type", "parsed")

    results = search_service.full_text_search(
        search_string,
        filters,
        page,
        page_size,
        sort_by_date,
        response_type=response_type,
    )
    return results


@router.post(
    "/details",
    summary="Fetch a curated record by CoLD ID including hop-1 relations",
    description=("Given a user-facing table and a CoLD ID, returns the canonical record and its first-hop related entries."),
    responses={
        200: {
            "description": "Flattened, mapping-transformed record.",
            "content": {
                "application/json": {
                    "example": {
                        "source_table": "Answers",
                        "id": "CHE_15-TC",
                        "Title": "…",
                        "hop1_relations": {},
                    }
                }
            },
        },
        404: {"description": "Record not found."},
    },
)
def handle_curated_details_search(body: CuratedDetailsRequest):
    table = body.table
    record_id = body.id
    response_type = getattr(body, "response_type", "parsed")

    results = search_service.curated_details_search(table, record_id, response_type=response_type)
    return results


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
def return_full_table(body: FullTableRequest):
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

    return results


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
def get_specialists_by_jurisdiction(jurisdiction_alpha_code: str):
    try:
        results = search_service.get_specialists_by_jurisdiction(jurisdiction_alpha_code)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
