from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel
from pydantic.alias_generators import to_camel, to_snake

from app.config import config
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
from app.services.database import Database

logger = logging.getLogger(__name__)

_SAFE_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_.]*$")
_SAFE_COLUMN = re.compile(r"^[a-z_][a-z0-9_]*$")


def _theme_exists_clause(slug: str, schema: str) -> str | None:
    """WHERE fragment using :theme, referencing base-view alias 'b'."""
    if slug == "literature":
        return (
            f'EXISTS (SELECT 1 FROM "{schema}"."_nc_m2m_Themes_Literature" m '
            f'JOIN "{schema}"."Themes" t ON t.id = m."Themes_id" '
            f'WHERE m."Literature_id" = b.id AND t."Theme" = :theme)'
        )
    if slug == "arbitral-awards":
        return (
            f'EXISTS (SELECT 1 FROM "{schema}"."_nc_m2m_Themes_Arbitral_Awards" m '
            f'JOIN "{schema}"."Themes" t ON t.id = m."Themes_id" '
            f'WHERE m."Arbitral_Awards_id" = b.id AND t."Theme" = :theme)'
        )
    if slug == "court-decisions":
        return (
            f'EXISTS (SELECT 1 FROM "{schema}"."_nc_m2m_Questions_Court_Decisions" qcd '
            f'JOIN "{schema}"."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = qcd."Questions_id" '
            f'JOIN "{schema}"."Themes" t ON t.id = tq."Themes_id" '
            f'WHERE qcd."Court_Decisions_id" = b.id AND t."Theme" = :theme)'
        )
    return None


@dataclass(frozen=True)
class EntityListConfig:
    slug: str
    table: str
    view: str
    relation_model: type[BaseModel]
    columns: tuple[str, ...]
    default_order_by: str
    default_order_dir: Literal["asc", "desc"] = "desc"
    has_jurisdiction: bool = True
    has_theme: bool = False
    extra_filter_columns: tuple[str, ...] = field(default_factory=tuple)


ENTITY_LIST_CONFIGS: dict[str, EntityListConfig] = {
    "court-decisions": EntityListConfig(
        slug="court-decisions",
        table="Court Decisions",
        view="data_views.base_court_decisions",
        relation_model=CourtDecisionRelation,
        columns=(
            "case_citation",
            "case_title",
            "date",
            "publication_date_iso",
            "jurisdictions_alpha_3_code",
        ),
        default_order_by="publication_date_iso",
        default_order_dir="desc",
        has_theme=True,
        extra_filter_columns=("case_rank",),
    ),
    "literature": EntityListConfig(
        slug="literature",
        table="Literature",
        view="data_views.base_literature",
        relation_model=LiteratureRelation,
        columns=("author", "title", "publication_year", "oup_jd_chapter"),
        default_order_by="publication_year",
        default_order_dir="desc",
        has_jurisdiction=False,
        has_theme=True,
    ),
    "domestic-instruments": EntityListConfig(
        slug="domestic-instruments",
        table="Domestic Instruments",
        view="data_views.base_domestic_instruments",
        relation_model=DomesticInstrumentRelation,
        columns=("title_in_english", "official_title", "abbreviation", "date"),
        default_order_by="date",
        default_order_dir="desc",
    ),
    "regional-instruments": EntityListConfig(
        slug="regional-instruments",
        table="Regional Instruments",
        view="data_views.base_regional_instruments",
        relation_model=RegionalInstrumentRelation,
        columns=("title", "abbreviation", "date"),
        default_order_by="date",
        default_order_dir="desc",
        has_jurisdiction=False,
    ),
    "international-instruments": EntityListConfig(
        slug="international-instruments",
        table="International Instruments",
        view="data_views.base_international_instruments",
        relation_model=InternationalInstrumentRelation,
        columns=("name", "date"),
        default_order_by="date",
        default_order_dir="desc",
        has_jurisdiction=False,
    ),
    "arbitral-awards": EntityListConfig(
        slug="arbitral-awards",
        table="Arbitral Awards",
        view="data_views.base_arbitral_awards",
        relation_model=ArbitralAwardRelation,
        columns=("case_number", "year", "seat_town", "source"),
        default_order_by="year",
        default_order_dir="desc",
        has_theme=True,
    ),
    "arbitral-institutions": EntityListConfig(
        slug="arbitral-institutions",
        table="Arbitral Institutions",
        view="data_views.base_arbitral_institutions",
        relation_model=ArbitralInstitutionRelation,
        columns=("institution", "abbreviation"),
        default_order_by="institution",
        default_order_dir="asc",
    ),
    "arbitral-rules": EntityListConfig(
        slug="arbitral-rules",
        table="Arbitral Rules",
        view="data_views.base_arbitral_rules",
        relation_model=ArbitralRuleRelation,
        columns=("set_of_rules", "in_force_from"),
        default_order_by="set_of_rules",
        default_order_dir="asc",
    ),
    "specialists": EntityListConfig(
        slug="specialists",
        table="Specialists",
        view="data_views.base_specialists",
        relation_model=SpecialistRelation,
        columns=("specialist", "affiliation"),
        default_order_by="specialist",
        default_order_dir="asc",
    ),
    "jurisdictions": EntityListConfig(
        slug="jurisdictions",
        table="Jurisdictions",
        view="data_views.base_jurisdictions",
        relation_model=JurisdictionRelation,
        columns=("name", "region", "legal_family"),
        default_order_by="name",
        default_order_dir="asc",
        has_jurisdiction=False,
    ),
    "questions": EntityListConfig(
        slug="questions",
        table="Questions",
        view="data_views.base_questions",
        relation_model=QuestionRelation,
        columns=("question", "question_number"),
        default_order_by="question_number",
        default_order_dir="asc",
        has_jurisdiction=False,
    ),
}


def list_entity_slugs() -> list[str]:
    return list(ENTITY_LIST_CONFIGS.keys())


def get_entity_config(slug: str) -> EntityListConfig | None:
    return ENTITY_LIST_CONFIGS.get(slug)


def _safe_column_for(cfg: EntityListConfig, value: str) -> str | None:
    snake = to_snake(value)
    if not _SAFE_COLUMN.match(snake):
        return None
    if snake in cfg.columns or snake == cfg.default_order_by or snake in cfg.extra_filter_columns:
        return snake
    if snake in {"id", "cold_id"}:
        return snake
    return None


def _to_camel_dict(row: dict[str, Any], cfg: EntityListConfig) -> dict[str, Any]:
    out: dict[str, Any] = {"id": row.get("id"), "cold_id": row.get("cold_id")}
    for col in cfg.columns:
        out[col] = row.get(col)
    return {to_camel(k): v for k, v in out.items()}


class EntityListService:
    def __init__(self) -> None:
        self.db = Database(config.SQL_CONN_STRING)

    def list_entity(
        self,
        cfg: EntityListConfig,
        *,
        jurisdiction: str | None = None,
        theme: str | None = None,
        page: int = 1,
        page_size: int = 200,
        order_by: str | None = None,
        order_dir: str | None = None,
        extra_filters: dict[str, str] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        if not _SAFE_IDENTIFIER.match(cfg.view):
            raise ValueError(f"Unsafe view identifier: {cfg.view}")

        where_parts: list[str] = []
        params: dict[str, Any] = {}

        if jurisdiction and cfg.has_jurisdiction:
            params["juris"] = jurisdiction.upper()
            where_parts.append("b.\"jurisdictions_alpha_3_code\" ILIKE '%' || :juris || '%'")

        schema = config.NOCODB_POSTGRES_SCHEMA
        if theme and cfg.has_theme and schema:
            theme_clause = _theme_exists_clause(cfg.slug, schema)
            if theme_clause:
                params["theme"] = theme
                where_parts.append(theme_clause)

        if extra_filters:
            for raw_key, raw_val in extra_filters.items():
                if raw_val is None or raw_val == "":
                    continue
                col = _safe_column_for(cfg, raw_key)
                if col is None or col not in cfg.extra_filter_columns:
                    continue
                p_name = f"f_{col}"
                params[p_name] = raw_val
                where_parts.append(f'b."{col}"::text = :{p_name}')

        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

        order_col = _safe_column_for(cfg, order_by) if order_by else cfg.default_order_by
        if order_col is None:
            order_col = cfg.default_order_by
        direction = (order_dir or cfg.default_order_dir).lower()
        if direction not in {"asc", "desc"}:
            direction = cfg.default_order_dir
        order_sql = f' ORDER BY b."{order_col}" {direction.upper()} NULLS LAST'

        page = max(1, page)
        page_size = max(1, min(250, page_size))
        offset = (page - 1) * page_size

        projection = ", ".join(f'b."{col}"' for col in ("id", "cold_id", *cfg.columns))
        list_sql = f"SELECT {projection} FROM {cfg.view} b{where_sql}{order_sql} LIMIT {page_size} OFFSET {offset}"
        count_sql = f"SELECT COUNT(*) AS n FROM {cfg.view} b{where_sql}"

        try:
            rows = self.db.execute_query(list_sql, params) or []
            count_rows = self.db.execute_query(count_sql, params) or []
            total = int(count_rows[0].get("n", 0)) if count_rows else 0
        except Exception:
            logger.exception("Failed to list entity slug=%s", cfg.slug)
            raise

        items = [_to_camel_dict(r, cfg) for r in rows]
        return items, total

    def count_all(self, jurisdiction: str | None = None) -> dict[str, int]:
        from app.services.entity_counts import COUNT_TABLES

        params: dict[str, Any] = {}
        unions: list[str] = []
        for key, view, has_jurisdiction in COUNT_TABLES:
            if not _SAFE_IDENTIFIER.match(view):
                continue
            where_sql = ""
            if jurisdiction and has_jurisdiction:
                params["juris"] = jurisdiction.upper()
                where_sql = " WHERE \"jurisdictions_alpha_3_code\" ILIKE '%' || :juris || '%'"
            unions.append(f"SELECT '{key}' AS k, COUNT(*) AS n FROM {view}{where_sql}")

        sql = " UNION ALL ".join(unions)
        try:
            rows = self.db.execute_query(sql, params) or []
        except Exception:
            logger.exception("Failed to compute entity counts")
            raise

        return {str(r.get("k")): int(r.get("n") or 0) for r in rows}
