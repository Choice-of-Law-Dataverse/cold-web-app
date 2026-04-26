from __future__ import annotations

import logging
from typing import Annotated, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.relations import (
    ArbitralAwardRelation,
    ArbitralInstitutionRelation,
    ArbitralRuleRelation,
    CourtDecisionRelation,
    DomesticInstrumentRelation,
    InternationalInstrumentRelation,
    JurisdictionRelation,
    LiteratureRelation,
    QuestionRelation,
    RegionalInstrumentRelation,
    SpecialistRelation,
)
from app.services.entity_list import (
    ENTITY_LIST_CONFIGS,
    EntityListService,
    list_entity_slugs,
)

logger = logging.getLogger(__name__)


type AnyEntityListItem = (
    ArbitralAwardRelation
    | ArbitralInstitutionRelation
    | ArbitralRuleRelation
    | CourtDecisionRelation
    | DomesticInstrumentRelation
    | InternationalInstrumentRelation
    | JurisdictionRelation
    | LiteratureRelation
    | QuestionRelation
    | RegionalInstrumentRelation
    | SpecialistRelation
)


class EntityListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[AnyEntityListItem]
    total: int
    page: int
    page_size: int


def get_entity_list_service() -> EntityListService:
    return EntityListService()


router = APIRouter(prefix="/entities", tags=["Entities"])


@router.get(
    "/{slug}",
    summary="List entities of a given type with optional jurisdiction filter",
    description=(
        "Returns a paginated, slim list of entities using the relation contract "
        "(`*Relation` shapes used inside detail responses). Supports jurisdiction "
        "filtering for entities that expose `jurisdictions_alpha_3_code`. "
        "Court Decisions additionally accepts a `case_rank` filter."
    ),
    response_model=EntityListResponse,
    responses={
        200: {"description": "Items, total, page, pageSize."},
        404: {"description": "Unknown entity slug."},
    },
)
def list_entity(
    slug: Annotated[str, Path(description="Entity slug, e.g. 'court-decisions'")],
    jurisdiction: Annotated[
        str | None,
        Query(description="Filter by jurisdiction Alpha-3 code (case-insensitive)."),
    ] = None,
    case_rank: Annotated[
        str | None,
        Query(description="Court Decisions only: filter by case rank."),
    ] = None,
    page: Annotated[int, Query(ge=1, description="1-indexed page number.")] = 1,
    page_size: Annotated[int, Query(ge=1, le=200, description="Items per page (max 200).")] = 200,
    order_by: Annotated[
        str | None,
        Query(description="Override default order column (snake or camelCase)."),
    ] = None,
    order_dir: Annotated[
        Literal["asc", "desc"] | None,
        Query(description="Override default order direction."),
    ] = None,
    service: EntityListService = Depends(get_entity_list_service),
) -> EntityListResponse:
    cfg = ENTITY_LIST_CONFIGS.get(slug)
    if cfg is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown entity '{slug}'. Known slugs: {list_entity_slugs()}",
        )

    extra: dict[str, str] = {}
    if case_rank is not None:
        extra["case_rank"] = case_rank

    try:
        items, total = service.list_entity(
            cfg,
            jurisdiction=jurisdiction,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir,
            extra_filters=extra,
        )
    except Exception as exc:
        logger.exception("Failed to list entity slug=%s", slug)
        raise HTTPException(status_code=500, detail="Failed to list entities") from exc

    parsed = [cast(AnyEntityListItem, cfg.relation_model.model_validate(item)) for item in items]
    return EntityListResponse(items=parsed, total=total, page=page, page_size=page_size)
