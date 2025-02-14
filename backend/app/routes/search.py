from fastapi import APIRouter, Depends, Request, HTTPException
from app.schemas.requests import (
    FullTextSearchRequest,
    CuratedDetailsRequest,
    FullTableRequest,
)
from app.services.search import SearchService
from app.auth import verify_jwt_token

search_service = SearchService()

router = APIRouter(
    prefix="/search", tags=["Search"], dependencies=[Depends(verify_jwt_token)]
)


@router.post("/")
def handle_full_text_search(request: Request, body: FullTextSearchRequest):
    search_string = body.search_string
    filters = body.filters or []

    results = search_service.full_text_search(search_string, filters)
    return results


@router.post("/details")
def handle_curated_details_search(request: Request, body: CuratedDetailsRequest):
    table = body.table
    record_id = body.id

    results = search_service.curated_details_search(table, record_id)
    return results


@router.post("/full_table")
def return_full_table(request: Request, body: FullTableRequest):
    table = body.table
    filters = body.filters or []

    if not table:
        raise HTTPException(status_code=400, detail="No table provided")

    try:
        if filters:
            results = search_service.filtered_table(table, filters)
        else:
            results = search_service.full_table(table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return results
