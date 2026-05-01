import logging
import re
from typing import Any

from pydantic.alias_generators import to_snake

from app.config import config
from app.services.database import Database
from app.services.filter_builder import build_filter_clause

_SAFE_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_.]*$")
_SAFE_COLUMN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self) -> None:
        self.db = Database(config.SQL_CONN_STRING)

    _TABLE_TO_VIEW: dict[str, str] = {
        "answers": "data_views.base_answers",
        "hcch answers": "data_views.base_hcch_answers",
        "court decisions": "data_views.base_court_decisions",
        "domestic instruments": "data_views.base_domestic_instruments",
        "domestic legal provisions": "data_views.base_domestic_legal_provisions",
        "regional instruments": "data_views.base_regional_instruments",
        "regional legal provisions": "data_views.base_regional_legal_provisions",
        "international instruments": "data_views.base_international_instruments",
        "international legal provisions": "data_views.base_international_legal_provisions",
        "literature": "data_views.base_literature",
        "arbitral awards": "data_views.base_arbitral_awards",
        "arbitral award": "data_views.base_arbitral_awards",
        "arbitration awards": "data_views.base_arbitral_awards",
        "arbitration award": "data_views.base_arbitral_awards",
        "arbitral institutions": "data_views.base_arbitral_institutions",
        "arbitral institution": "data_views.base_arbitral_institutions",
        "arbitration institutions": "data_views.base_arbitral_institutions",
        "arbitration institution": "data_views.base_arbitral_institutions",
        "arbitral rules": "data_views.base_arbitral_rules",
        "arbitration rules": "data_views.base_arbitral_rules",
        "arbitral provisions": "data_views.base_arbitral_provisions",
        "arbitral provision": "data_views.base_arbitral_provisions",
        "arbitration provisions": "data_views.base_arbitral_provisions",
        "arbitration provision": "data_views.base_arbitral_provisions",
        "jurisdictions": "data_views.base_jurisdictions",
        "questions": "data_views.base_questions",
        "specialists": "data_views.base_specialists",
    }

    _TABLE_TO_FTS_ENRICHMENT: dict[str, tuple[str, dict[str, str]]] = {
        "answers": (
            "data_views.answers",
            {"question": "Questions", "jurisdictions": "Jurisdictions", "themes": "Themes"},
        ),
        "hcch answers": ("data_views.hcch_answers", {"themes": "Themes"}),
        "court decisions": (
            "data_views.court_decisions",
            {"jurisdictions": "Jurisdictions", "themes": "Themes"},
        ),
        "domestic instruments": (
            "data_views.domestic_instruments",
            {"jurisdictions": "Jurisdictions"},
        ),
        "literature": (
            "data_views.literature",
            {"themes": "Themes"},
        ),
    }

    def _complete_view_for_table(self, table: str) -> str:
        if not table:
            raise ValueError("No table provided")
        view = self._TABLE_TO_VIEW.get(table.strip().lower())
        if not view or not _SAFE_IDENTIFIER.match(view):
            raise ValueError(f"Unsupported table for full/filtered query: {table}")
        return view

    def _fts_enrichment_for_table(self, table: str) -> tuple[str, dict[str, str]] | None:
        enrichment = self._TABLE_TO_FTS_ENRICHMENT.get(table.strip().lower())
        if not enrichment:
            return None
        view, fields = enrichment
        if not _SAFE_IDENTIFIER.match(view):
            return None
        if any(not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k) for k in fields):
            return None
        if any(not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", v) for v in fields.values()):
            return None
        return view, fields

    @staticmethod
    def _build_order_clause(alias: str, order_by: str | None, order_dir: str | None) -> str:
        if not order_by:
            return ""
        snake = to_snake(order_by)
        if not _SAFE_COLUMN.match(snake):
            return ""
        direction = "ASC" if (order_dir or "desc").lower() == "asc" else "DESC"
        return f' ORDER BY {alias}."{snake}" {direction} NULLS LAST'

    @staticmethod
    def _build_limit_clause(limit: int | None) -> str:
        if limit is None or limit <= 0:
            return ""
        return f" LIMIT {int(limit)}"

    def _build_select_sql(
        self,
        table: str,
        alias: str = "c",
        where_sql: str = "",
        order_by: str | None = None,
        order_dir: str | None = None,
        limit: int | None = None,
    ) -> str:
        view = self._complete_view_for_table(table)
        enrichment = self._fts_enrichment_for_table(table)
        order_sql = self._build_order_clause(alias, order_by, order_dir)
        limit_sql = self._build_limit_clause(limit)
        if enrichment is None:
            return (
                f"SELECT {alias}.id AS record_id, to_jsonb({alias}.*) AS complete_record "
                f"FROM {view} {alias}{where_sql}{order_sql}{limit_sql}"
            )
        fts_view, fields = enrichment
        pairs = ", ".join(f"'{key}', sv.\"{col}\"" for key, col in fields.items())
        return (
            f"SELECT {alias}.id AS record_id, "
            f"to_jsonb({alias}.*) || jsonb_build_object({pairs}) AS complete_record "
            f"FROM {view} {alias} "
            f"LEFT JOIN {fts_view} sv ON sv.id = {alias}.id"
            f"{where_sql}{order_sql}{limit_sql}"
        )

    VALID_DETAIL_TABLES: set[str] = {
        "Answers",
        "HCCH Answers",
        "Questions",
        "Court Decisions",
        "Domestic Instruments",
        "Domestic Legal Provisions",
        "Regional Instruments",
        "Regional Legal Provisions",
        "International Instruments",
        "International Legal Provisions",
        "Literature",
        "Arbitral Awards",
        "Arbitral Institutions",
        "Arbitral Rules",
        "Arbitral Provisions",
        "Jurisdictions",
        "Specialists",
    }

    def get_entity_detail(self, table: str, cold_id: str) -> dict[str, Any] | None:
        if table not in self.VALID_DETAIL_TABLES:
            raise ValueError(f"Unsupported table: {table}")

        sql = """
        SELECT source_table, record_id, cold_id, base_record, relations
        FROM data_views.get_entity_detail(:table_name, :cold_id)
        """
        params = {"table_name": table, "cold_id": cold_id}
        results = self.db.execute_query(sql, params)

        if not results:
            return None

        row = results[0]
        if row.get("record_id") is None:
            return None

        base_record = row.get("base_record") or {}

        return {
            "source_table": row.get("source_table"),
            "id": row.get("record_id"),
            "cold_id": row.get("cold_id"),
            **base_record,
            "relations": row.get("relations") or {},
        }

    @staticmethod
    def _flatten_rows(rows: list[dict[str, Any]], table: str, response_type: str) -> list[dict[str, Any]]:
        if response_type == "raw":
            return [row.get("complete_record") or {} for row in rows]

        results: list[dict[str, Any]] = []
        for row in rows:
            complete = row.get("complete_record") or {}
            flat: dict[str, Any] = {"source_table": table, "id": row.get("record_id")}
            for k, v in complete.items():
                if k == "id":
                    continue
                flat[k] = v
            if flat.get("cold_id"):
                flat["id"] = flat["cold_id"]
            else:
                flat["cold_id"] = flat["id"]
            if response_type == "both":
                results.append({"parsed": flat, "raw": complete})
            else:
                results.append(flat)
        return results

    def full_table(
        self,
        table: str,
        response_type: str = "parsed",
        order_by: str | None = None,
        order_dir: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            sql = self._build_select_sql(
                table,
                order_by=order_by,
                order_dir=order_dir,
                limit=limit,
            )
            rows = self.db.execute_query(sql, {}) or []
            return self._flatten_rows(rows, table, response_type)
        except Exception as e:
            logger.error("Error querying full table %s: %s", table, e)
            return []

    def filtered_table(
        self,
        table: str,
        filters: list[Any],
        response_type: str = "parsed",
        order_by: str | None = None,
        order_dir: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            alias = "c"
            where_sql, params = build_filter_clause(alias, filters)
            sql = self._build_select_sql(
                table,
                alias=alias,
                where_sql=where_sql,
                order_by=order_by,
                order_dir=order_dir,
                limit=limit,
            )
            rows = self.db.execute_query(sql, params) or []
            return self._flatten_rows(rows, table, response_type)
        except Exception as e:
            logger.error(
                "Error querying filtered table %s with filters %s: %s",
                table,
                filters,
                e,
            )
            return []

    def _extract_filters(self, filters: list[Any]) -> tuple[list[str], list[str], list[str]]:
        tables = []
        jurisdictions = []
        themes = []

        for filter_item in filters:
            column = filter_item.column
            raw_values = filter_item.values
            values = raw_values if isinstance(raw_values, list) else [raw_values] if raw_values is not None else []

            if column and values:
                col_lower = column.lower()
                if col_lower in [
                    "name (from jurisdiction)",
                    "jurisdiction name",
                    "jurisdictions",
                    "jurisdiction",
                ]:
                    jurisdictions.extend(values)
                elif col_lower in ["themes", "themes name"]:
                    themes.extend(values)
                elif col_lower in ["source_table", "tables"]:
                    tables.extend(values)
        return tables, jurisdictions, themes

    def full_text_search(
        self,
        search_string: str | None,
        filters: list[Any] | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_by_date: bool = False,
        response_type: str = "parsed",
    ) -> dict[str, Any]:
        if filters is None:
            filters = []
        tables, jurisdictions, themes = self._extract_filters(filters)
        params = {
            "search_term": search_string,
            "filter_tables": tables or None,
            "filter_jurisdictions": jurisdictions or None,
            "filter_themes": themes or None,
            "page": page,
            "page_size": page_size,
            "sort_by_date": sort_by_date,
        }
        count_sql = (
            "SELECT data_views.search_all_count_v2("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[])"
            ") AS total_matches"
        )
        count_result = self.db.execute_query(count_sql, params)
        total_matches = count_result[0].get("total_matches", 0) if count_result else 0
        logger.debug("Performing full-text search with params: %s", params)
        sql = (
            "SELECT table_name AS source_table, record_id AS id, complete_record AS complete_record, rank, result_date "
            "FROM data_views.search_all_v2("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(:page AS integer), "
            "page_size := CAST(:page_size AS integer), "
            "sort_by_date := CAST(:sort_by_date AS boolean)"
            ")"
        )
        rows = self.db.execute_query(sql, params) or []
        logger.debug("search_all_v2 returned %d rows (total_matches=%d)", len(rows), total_matches)
        if not rows and total_matches > 0:
            logger.warning("search SQL:\n%s\nparams: %s", sql, params)
        parsed_results = []
        raw_results = []
        for row in rows:
            complete = row.get("complete_record") or {}
            if response_type in ("parsed", "both"):
                flat: dict[str, Any] = {
                    "source_table": row.get("source_table"),
                    "id": row.get("id"),
                    "rank": row.get("rank"),
                    "result_date": row.get("result_date"),
                }
                for key, value in complete.items():
                    if key == "id":
                        continue
                    flat[key] = value
                if flat.get("cold_id"):
                    flat["id"] = flat["cold_id"]
                else:
                    flat["cold_id"] = flat["id"]
                parsed_results.append(flat)

            if response_type in ("raw", "both"):
                raw_results.append(
                    {
                        "source_table": row.get("source_table"),
                        "id": row.get("id"),
                        "rank": row.get("rank"),
                        "result_date": row.get("result_date"),
                        "complete_record": complete,
                    }
                )

        if response_type == "raw":
            return {
                "query": search_string,
                "filters": filters,
                "total_matches": total_matches,
                "page": page,
                "page_size": page_size,
                "results": raw_results,
            }
        if response_type == "both":
            combined = [{"parsed": p, "raw": r} for p, r in zip(parsed_results, raw_results, strict=False)]
            return {
                "query": search_string,
                "filters": filters,
                "total_matches": total_matches,
                "page": page,
                "page_size": page_size,
                "results": combined,
            }

        return {
            "query": search_string,
            "filters": filters,
            "total_matches": total_matches,
            "page": page,
            "page_size": page_size,
            "results": parsed_results,
        }

    def get_specialists_by_jurisdiction(self, jurisdiction_alpha_code: str) -> list[dict[str, Any]]:
        schema = config.NOCODB_POSTGRES_SCHEMA
        query = f"""
            SELECT s.*
            FROM {schema}."Specialists" s
            INNER JOIN {schema}."_nc_m2m_Jurisdictions_Specialists" js
                ON s.id = js."Specialists_id"
            INNER JOIN {schema}."Jurisdictions" j
                ON j.id = js."Jurisdictions_id"
            WHERE j."Alpha_3_Code" = :jurisdiction_alpha_code
            ORDER BY s."Specialist"
        """

        try:
            results = self.db.execute_query(query, {"jurisdiction_alpha_code": jurisdiction_alpha_code})
            return results or []
        except Exception as e:
            logger.error(f"Error querying specialists for jurisdiction {jurisdiction_alpha_code}: {e}")
            raise
