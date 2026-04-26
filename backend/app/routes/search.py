import logging
import re
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic.alias_generators import to_camel

from app.auth import verify_frontend_request
from app.schemas.details import TABLE_DETAIL_MODELS, AnyDetail, DetailBase
from app.schemas.records import AnyRecord, validate_record
from app.schemas.requests import (
    CuratedDetailsRequest,
    FilterValue,
    FTFilterOption,
    FTSFilterOption,
    FullTableRequest,
    FullTextSearchRequest,
)
from app.schemas.responses import FullTextSearchResponse, SpecialistResponse
from app.schemas.search_result import validate_search_result
from app.services.search import SearchService

logger = logging.getLogger(__name__)


def _normalize_to_camel(key: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return to_camel(s.lower().rstrip("_"))


def _camel_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {_normalize_to_camel(k): _camel_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_camel_keys(item) for item in obj]
    return obj


def _coerce_filter_value(raw: str) -> FilterValue:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if raw and re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def _parse_full_table_filter(raw: str) -> FTFilterOption:
    if ":" not in raw:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filter '{raw}': expected format 'column:value' or 'column:val1,val2'",
        )
    column, _, value_part = raw.partition(":")
    column = column.strip()
    if not column:
        raise HTTPException(status_code=400, detail=f"Invalid filter '{raw}': column is empty")
    parts = [v.strip() for v in value_part.split(",")] if "," in value_part else [value_part]
    coerced = [_coerce_filter_value(v) for v in parts]
    value: FilterValue | list[FilterValue] = coerced[0] if len(coerced) == 1 else coerced
    return FTFilterOption(column=column, value=value)


def get_search_service() -> SearchService:
    """Dependency function to lazily instantiate the SearchService."""
    return SearchService()


router = APIRouter(
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(verify_frontend_request)],
)


def _do_full_text_search(
    search_string: str | None,
    filters: list[FTSFilterOption],
    page: int,
    page_size: int,
    sort_by_date: bool,
    search_service: SearchService,
) -> FullTextSearchResponse:
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


def _do_entity_detail(table: str, cold_id: str, search_service: SearchService) -> AnyDetail:
    try:
        result = search_service.get_entity_detail(table, cold_id)
    except ValueError as e:
        logger.warning("Invalid entity detail request: table=%s id=%s: %s", table, cold_id, e)
        raise HTTPException(status_code=400, detail="Invalid request parameters") from e
    if not result:
        raise HTTPException(status_code=404, detail=f"No record found for {cold_id} in {table}")
    model = TABLE_DETAIL_MODELS.get(result.get("source_table", ""), DetailBase)
    return model.model_validate(result)


def _do_full_table(
    table: str,
    filters: list[FTFilterOption],
    order_by: str | None,
    order_dir: str | None,
    limit: int | None,
    search_service: SearchService,
) -> list[AnyRecord]:
    if not table:
        raise HTTPException(status_code=400, detail="No table provided")
    try:
        if filters:
            results = search_service.filtered_table(
                table,
                filters,
                response_type="parsed",
                order_by=order_by,
                order_dir=order_dir,
                limit=limit,
            )
        else:
            results = search_service.full_table(
                table,
                response_type="parsed",
                order_by=order_by,
                order_dir=order_dir,
                limit=limit,
            )
    except Exception as e:
        logger.exception("Failed to query table=%s filters=%d", table, len(filters))
        raise HTTPException(status_code=500, detail="Failed to query table") from e

    return [validate_record(_camel_keys(r)) for r in results]


_FULL_TEXT_SEARCH_RESPONSES: dict[int | str, dict[str, Any]] = {
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
}

_FULL_TEXT_SEARCH_DESCRIPTION = (
    "Searches across multiple domains (Answers, HCCH Answers, Court Decisions, Domestic Instruments, "
    "Regional Instruments, International Instruments, Literature, Arbitral Awards, and Arbitral Rules). "
    "Filters support user-facing fields like 'tables', 'Jurisdictions', or 'Themes'. "
    "You can sort by date and paginate results."
)


@router.post(
    "/",
    summary="Full-text search across CoLD data",
    description=_FULL_TEXT_SEARCH_DESCRIPTION,
    responses=_FULL_TEXT_SEARCH_RESPONSES,
)
def handle_full_text_search(
    body: FullTextSearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> FullTextSearchResponse:
    response_type = body.response_type or "parsed"
    if response_type != "parsed":
        raise HTTPException(
            status_code=400,
            detail="Only response_type='parsed' is supported for typed search results",
        )
    return _do_full_text_search(
        body.search_string,
        body.filters or [],
        body.page,
        body.page_size,
        body.sort_by_date or False,
        search_service,
    )


@router.get(
    "/",
    summary="Full-text search across CoLD data (GET alternative)",
    description=(
        f"{_FULL_TEXT_SEARCH_DESCRIPTION}\n\n"
        "Filter columns are exposed as dedicated repeatable query parameters: "
        "`tables`, `jurisdictions`, `themes`. Pass each value separately, e.g. "
        "`?tables=Answers&tables=Court%20Decisions&jurisdictions=Switzerland`."
    ),
    responses=_FULL_TEXT_SEARCH_RESPONSES,
)
def handle_full_text_search_get(
    search_string: Annotated[str | None, Query(description="Free-text query string")] = None,
    tables: Annotated[list[str] | None, Query(description="Restrict to source tables (repeatable)")] = None,
    jurisdictions: Annotated[list[str] | None, Query(description="Filter by jurisdictions (repeatable)")] = None,
    themes: Annotated[list[str] | None, Query(description="Filter by themes (repeatable)")] = None,
    page: Annotated[int, Query(ge=1, description="Page number, must be >= 1")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Number of results per page")] = 50,
    sort_by_date: Annotated[bool, Query(description="Sort results by date descending if True.")] = False,
    search_service: SearchService = Depends(get_search_service),
) -> FullTextSearchResponse:
    filters: list[FTSFilterOption] = []
    if tables:
        filters.append(FTSFilterOption(column="tables", values=tables))
    if jurisdictions:
        filters.append(FTSFilterOption(column="jurisdictions", values=jurisdictions))
    if themes:
        filters.append(FTSFilterOption(column="themes", values=themes))
    return _do_full_text_search(search_string, filters, page, page_size, sort_by_date, search_service)


_ENTITY_DETAIL_RESPONSES: dict[int | str, dict[str, Any]] = {404: {"description": "Record not found."}}
_ENTITY_DETAIL_DESCRIPTION = (
    "Given a table and a CoLD ID, returns the record with all first-hop relations in a standardized shape."
)


@router.post(
    "/details",
    summary="Fetch a curated record by CoLD ID including relations",
    description=_ENTITY_DETAIL_DESCRIPTION,
    response_model=AnyDetail,
    responses=_ENTITY_DETAIL_RESPONSES,
)
def handle_entity_detail(
    body: CuratedDetailsRequest,
    search_service: SearchService = Depends(get_search_service),
) -> AnyDetail:
    return _do_entity_detail(body.table, body.id, search_service)


@router.get(
    "/details",
    summary="Fetch a curated record by CoLD ID (GET alternative)",
    description=_ENTITY_DETAIL_DESCRIPTION,
    response_model=AnyDetail,
    responses=_ENTITY_DETAIL_RESPONSES,
)
def handle_entity_detail_get(
    table: Annotated[str, Query(description="Source table name (e.g. 'Answers')")],
    cold_id: Annotated[str, Query(alias="id", description="CoLD ID for the record")],
    search_service: SearchService = Depends(get_search_service),
) -> AnyDetail:
    return _do_entity_detail(table, cold_id, search_service)


_FULL_TABLE_RESPONSES: dict[int | str, dict[str, Any]] = {
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
}
_FULL_TABLE_DESCRIPTION = (
    "Returns all records from the specified table or a filtered subset. "
    "Filters accept user-facing field names and values (mapping-aware)."
)


@router.post(
    "/full_table",
    summary="Return full or filtered table",
    description=_FULL_TABLE_DESCRIPTION,
    responses=_FULL_TABLE_RESPONSES,
)
def return_full_table(
    body: FullTableRequest,
    search_service: SearchService = Depends(get_search_service),
) -> list[AnyRecord]:
    return _do_full_table(
        body.table,
        body.filters or [],
        body.order_by,
        body.order_dir,
        body.limit,
        search_service,
    )


@router.get(
    "/full_table",
    summary="Return full or filtered table (GET alternative)",
    description=(
        f"{_FULL_TABLE_DESCRIPTION}\n\n"
        "Filters use the repeatable `filter` query parameter with format `column:value` "
        "or `column:val1,val2` for multiple values. Values matching `true`/`false` are "
        "parsed as booleans; pure-digit strings as integers; everything else stays a string. "
        "Example: `?table=Court%20Decisions&filter=caseRank:10&filter=jurisdiction:Switzerland`."
    ),
    responses=_FULL_TABLE_RESPONSES,
)
def return_full_table_get(
    table: Annotated[str, Query(description="Source table name")],
    filter_: Annotated[
        list[str] | None,
        Query(
            alias="filter",
            description="Filter as 'column:value' or 'column:val1,val2'. Repeatable.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Query(ge=1, le=10000, description="Maximum number of rows to return. Omit for no limit."),
    ] = None,
    order_by: Annotated[
        str | None,
        Query(description="Column name to sort by (camelCase or snake_case). Unknown columns are ignored."),
    ] = None,
    order_dir: Annotated[
        Literal["asc", "desc"] | None,
        Query(description="Sort direction when order_by is provided."),
    ] = "desc",
    search_service: SearchService = Depends(get_search_service),
) -> list[AnyRecord]:
    filters = [_parse_full_table_filter(f) for f in (filter_ or [])]
    return _do_full_table(table, filters, order_by, order_dir, limit, search_service)


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
        logger.exception("Failed to fetch specialists for jurisdiction=%s", jurisdiction_alpha_code)
        raise HTTPException(status_code=500, detail="Failed to fetch specialists") from e
