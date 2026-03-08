import logging
from typing import Any

from app.config import config
from app.services.database import Database
from app.services.filter_builder import build_filter_clause

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)

    def _complete_view_for_table(self, table: str) -> str:
        if not table:
            raise ValueError("No table provided")

        normalized = table.strip().lower()

        canonical = {
            "answers": "Answers",
            "hcch answers": "HCCH Answers",
            "court decisions": "Court Decisions",
            "domestic instruments": "Domestic Instruments",
            "domestic legal provisions": "Domestic Legal Provisions",
            "regional instruments": "Regional Instruments",
            "regional legal provisions": "Regional Legal Provisions",
            "international instruments": "International Instruments",
            "international legal provisions": "International Legal Provisions",
            "literature": "Literature",
            "arbitral awards": "Arbitral Awards",
            "arbitral award": "Arbitral Awards",
            "arbitration awards": "Arbitral Awards",
            "arbitration award": "Arbitral Awards",
            "arbitral institutions": "Arbitral Institutions",
            "arbitral institution": "Arbitral Institutions",
            "arbitration institutions": "Arbitral Institutions",
            "arbitration institution": "Arbitral Institutions",
            "arbitral rules": "Arbitral Rules",
            "arbitration rules": "Arbitral Rules",
            "arbitral provisions": "Arbitral Provisions",
            "arbitral provision": "Arbitral Provisions",
            "arbitration provisions": "Arbitral Provisions",
            "arbitration provision": "Arbitral Provisions",
            "jurisdictions": "Jurisdictions",
            "questions": "Questions",
        }

        table_key = canonical.get(normalized)
        if not table_key:
            raise ValueError(f"Unsupported table for full/filtered query: {table}")

        mapping = {
            "Answers": "data_views.base_answers",
            "HCCH Answers": "data_views.base_hcch_answers",
            "Court Decisions": "data_views.base_court_decisions",
            "Domestic Instruments": "data_views.base_domestic_instruments",
            "Domestic Legal Provisions": "data_views.base_domestic_legal_provisions",
            "Regional Instruments": "data_views.base_regional_instruments",
            "Regional Legal Provisions": "data_views.base_regional_legal_provisions",
            "International Instruments": "data_views.base_international_instruments",
            "International Legal Provisions": "data_views.base_international_legal_provisions",
            "Literature": "data_views.base_literature",
            "Arbitral Awards": "data_views.base_arbitral_awards",
            "Arbitral Institutions": "data_views.base_arbitral_institutions",
            "Arbitral Rules": "data_views.base_arbitral_rules",
            "Arbitral Provisions": "data_views.base_arbitral_provisions",
            "Jurisdictions": "data_views.base_jurisdictions",
            "Questions": "data_views.base_questions",
        }

        view = mapping.get(table_key)
        if not view:
            raise ValueError(f"Unsupported table for full/filtered query: {table}")
        return view

    def get_entity_detail(self, table: str, cold_id: str) -> dict[str, Any] | None:
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

    def full_table(self, table, response_type: str = "parsed"):
        try:
            view = self._complete_view_for_table(table)
            sql = f"SELECT c.id AS record_id, to_jsonb(c.*) AS complete_record FROM {view} c"
            rows = self.db.execute_query(sql, {}) or []

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
                if response_type == "both":
                    results.append({"parsed": flat, "raw": complete})
                else:
                    results.append(flat)
            return results
        except Exception as e:
            logger.error("Error querying full table %s: %s", table, e)
            return []

    def filtered_table(self, table, filters, response_type: str = "parsed"):
        try:
            view = self._complete_view_for_table(table)
            alias = "c"
            where_sql, params = build_filter_clause(alias, filters)
            sql = f"SELECT {alias}.id AS record_id, to_jsonb({alias}.*) AS complete_record FROM {view} {alias}{where_sql}"
            rows = self.db.execute_query(sql, params) or []

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
                if response_type == "both":
                    results.append({"parsed": flat, "raw": complete})
                else:
                    results.append(flat)
            return results
        except Exception as e:
            logger.error(
                "Error querying filtered table %s with filters %s: %s",
                table,
                filters,
                e,
            )
            return []

    def _extract_filters(self, filters):
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
        search_string,
        filters=None,
        page=1,
        page_size=50,
        sort_by_date=False,
        response_type: str = "parsed",
    ):
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
        logger.warning("search_all_v2 returned %d rows (total_matches=%d)", len(rows), total_matches)
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
        query = """
            SELECT s.*
            FROM p1q5x3pj29vkrdr."Specialists" s
            INNER JOIN p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Specialists" js
                ON s.id = js."Specialists_id"
            INNER JOIN p1q5x3pj29vkrdr."Jurisdictions" j
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
