from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import verify_jwt_token
from app.schemas.requests import (
    CuratedDetailsRequest,
    FullTableRequest,
    FullTextSearchRequest,
)
from app.services.search import SearchService

search_service = SearchService()

router = APIRouter(
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(verify_jwt_token)],
)


@router.post(
    "/",
    summary="Full-text search across CoLD data",
    description=(
        "Searches across multiple domains (Answers, HCCH Answers, Court Decisions, Domestic Instruments, Regional Instruments, International Instruments, and Literature). "
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
                        "results": [{"source_table": "Answers", "id": "CHE_15-TC", "Title": "…"}, {"source_table": "Court Decisions", "id": "CD-GBR-1167", "Title": "…"}],
                    }
                }
            },
        }
    },
)
def handle_full_text_search(request: Request, body: FullTextSearchRequest):
    search_string = body.search_string
    filters = body.filters or []
    page = body.page
    page_size = body.page_size
    sort_by_date = getattr(body, "sort_by_date", False)
    response_type = getattr(body, "response_type", "parsed")

    results = search_service.full_text_search(search_string, filters, page, page_size, sort_by_date, response_type=response_type)
    return results


@router.post(
    "/details",
    summary="Fetch a curated record by CoLD ID including hop-1 relations",
    description=("Given a user-facing table and a CoLD ID, returns the canonical record and its first-hop related entries."),
    responses={
        200: {
            "description": "Flattened, mapping-transformed record.",
            "content": {"application/json": {"example": {"source_table": "Answers", "id": "CHE_15-TC", "Title": "…", "hop1_relations": {}}}},
        },
        404: {"description": "Record not found."},
    },
)
def handle_curated_details_search(request: Request, body: CuratedDetailsRequest):
    table = body.table
    record_id = body.id
    response_type = getattr(body, "response_type", "parsed")

    results = search_service.curated_details_search(table, record_id, response_type=response_type)
    return results


@router.post(
    "/full_table",
    summary="Return full or filtered table",
    description=("Returns all records from the specified table or a filtered subset. Filters accept user-facing field names and values (mapping-aware)."),
    responses={
        200: {
            "description": "Array of transformed records from the requested table.",
            "content": {"application/json": {"example": [{"source_table": "Answers", "id": "CHE_15-TC", "Jurisdictions": ["Switzerland"], "Title": "…"}]}},
        },
        400: {"description": "Missing or invalid table parameter."},
        500: {"description": "Server error while querying the table."},
    },
)
def return_full_table(request: Request, body: FullTableRequest):
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
