import json
import logging
from typing import Any

from app.config import config
from app.services.configurable_transformer import get_configurable_transformer
from app.services.database import Database
from app.services.mapping_repository import get_mapping_repository
from app.services.transformers import DataTransformerFactory

# logger for this module
logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.test = config.TEST
        self.mapping_repo = get_mapping_repository()
        self.configurable_transformer = get_configurable_transformer()

    # ------------------------------
    # Helper utilities
    # ------------------------------
    def _complete_view_for_table(self, table: str) -> str:
        """
        Map user-facing table names (case-insensitive; supports common singular/plural variants)
        to data_views <table>_complete view names.
        """
        if not table:
            raise ValueError("No table provided")

        normalized = table.strip().lower()

        # Canonical names
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
            # Arbitration domain (support plural and singular, and common synonyms)
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
            "Answers": "data_views.answers_complete",
            "HCCH Answers": "data_views.hcch_answers_complete",
            "Court Decisions": "data_views.court_decisions_complete",
            "Domestic Instruments": "data_views.domestic_instruments_complete",
            "Domestic Legal Provisions": "data_views.domestic_legal_provisions_complete",
            "Regional Instruments": "data_views.regional_instruments_complete",
            "Regional Legal Provisions": "data_views.regional_legal_provisions_complete",
            "International Instruments": "data_views.international_instruments_complete",
            "International Legal Provisions": "data_views.international_legal_provisions_complete",
            "Literature": "data_views.literature_complete",
            "Arbitral Awards": "data_views.arbitral_awards_complete",
            "Arbitral Institutions": "data_views.arbitral_institutions_complete",
            "Arbitral Rules": "data_views.arbitral_rules_complete",
            "Arbitral Provisions": "data_views.arbitral_provisions_complete",
            "Jurisdictions": "data_views.jurisdictions_complete",
            "Questions": "data_views.questions_complete",
        }

        view = mapping.get(table_key)
        if not view:
            raise ValueError(f"Unsupported table for full/filtered query: {table}")
        return view

    def _quote_ident(self, name: str) -> str:
        """Quote an identifier for SQL (simple double-quote escaping)."""
        return '"' + name.replace('"', '""') + '"'

    def _quote_json_key(self, key: str) -> str:
        """Quote a JSON object key as a SQL string literal."""
        return "'" + key.replace("'", "''") + "'"

    def _prepare_boolean_value(self, table: str, column: str, user_value: Any) -> Any:
        """
        If the column corresponds to a boolean mapping target in the table mapping,
        convert user-faced value (e.g., "Yes"/"None") into boolean True/False.
        Otherwise, return value unchanged.
        """
        mapping_conf = self.mapping_repo.get_mapping(table) or {}
        bool_maps = (mapping_conf.get("mappings") or {}).get("boolean_mappings") or {}
        bm = bool_maps.get(column)
        if not bm:
            # also check nested boolean mappings (inside nested_mappings)
            nested = (mapping_conf.get("mappings") or {}).get("nested_mappings") or {}
            for _k, nm in nested.items():
                nbm = (nm or {}).get("boolean_mappings") or {}
                if column in nbm:
                    bm = nbm[column]
                    break
        if bm:
            true_val = bm.get("true_value")
            false_val = bm.get("false_value")
            if isinstance(user_value, str):
                if true_val is not None and user_value == true_val:
                    return True
                if false_val is not None and user_value == false_val:
                    return False
            # if already boolean, keep it
            if isinstance(user_value, bool):
                return user_value
        return user_value

    def _build_filter_sql(self, table: str, alias: str, filters) -> tuple[str, dict[str, Any]]:
        """
        Build SQL WHERE clause and params from user-faced filters using reverse mapping,
        including nested array JSONB access for paths like related_array.Field.

        Returns: (where_sql, params)
        """
        if not filters:
            return "", {}

        reverse_mapping = self.configurable_transformer.get_reverse_field_mapping(table) or {}

        clauses: list[str] = []
        params: dict[str, Any] = {}

        def normalize_column(col: str) -> str:
            # Support columns ending with '?' by stripping it if needed
            if col not in reverse_mapping and col.endswith("?"):
                alt = col[:-1]
                if alt in reverse_mapping:
                    return alt
            return col

        for i, f in enumerate(filters):
            # Support both pydantic model with attributes and plain dicts
            col = getattr(f, "column", None) if hasattr(f, "column") else f.get("column")
            raw_val = getattr(f, "value", None) if hasattr(f, "value") else f.get("value")
            if col is None:
                continue

            col = normalize_column(col)
            source_path = reverse_mapping.get(col, col)  # fall back to provided name
            # convert boolean user-faced values if applicable
            if isinstance(raw_val, list):
                conv_values = [self._prepare_boolean_value(table, col, v) for v in raw_val]
            else:
                conv_values = [self._prepare_boolean_value(table, col, raw_val)]

            # Build OR for multiple values
            or_parts: list[str] = []
            for j, v in enumerate(conv_values):
                p_name = f"p_{i}_{j}"
                # Nested path: e.g., related_jurisdictions.Name
                if "." in source_path:
                    arr_name, field_name = source_path.split(".", 1)
                    arr_sql = f"{alias}.{self._quote_ident(arr_name)}"
                    # EXISTS over jsonb array
                    if isinstance(v, str):
                        or_parts.append(
                            f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem WHERE elem->>{self._quote_json_key(field_name)} ILIKE '%' || :{p_name} || '%')"  # noqa: E501
                        )
                        params[p_name] = v
                    elif isinstance(v, bool):
                        # Compare boolean by casting text to boolean
                        or_parts.append(
                            f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem WHERE (elem->>{self._quote_json_key(field_name)})::boolean = :{p_name})"  # noqa: E501
                        )
                        params[p_name] = v
                    elif isinstance(v, (int, float)):
                        # numeric compare: cast to numeric where possible
                        or_parts.append(
                            f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem WHERE (elem->>{self._quote_json_key(field_name)})::numeric = :{p_name})"  # noqa: E501
                        )
                        params[p_name] = v
                    else:
                        # fallback to text match
                        or_parts.append(
                            f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem WHERE elem->>{self._quote_json_key(field_name)} = :{p_name})"  # noqa: E501
                        )
                        params[p_name] = str(v)
                else:
                    col_sql = f"{alias}.{self._quote_ident(source_path)}"
                    if isinstance(v, str):
                        or_parts.append(f"{col_sql} ILIKE '%' || :{p_name} || '%'")
                        params[p_name] = v
                    elif isinstance(v, bool):
                        or_parts.append(f"{col_sql} = :{p_name}")
                        params[p_name] = v
                    elif isinstance(v, (int, float)):
                        or_parts.append(f"{col_sql} = :{p_name}")
                        params[p_name] = v
                    else:
                        # fallback as text equality
                        or_parts.append(f"{col_sql}::text = :{p_name}")
                        params[p_name] = json.dumps(v)

            if or_parts:
                clauses.append("(" + " OR ".join(or_parts) + ")")

        where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        return where_sql, params

    def curated_details_search(self, table, cold_id, response_type: str = "parsed"):
        """
        Fetch a single record by table and CoLD_ID using the new search_for_entry SQL function.
        Returns the complete record along with hop-1 (directly related) entries, transformed
        similar to full text search results.
        """
        try:
            sql = """
            SELECT found_table, record_id, complete_record, hop1_relations
            FROM data_views.search_for_entry(:table_name, :cold_id)
            """
            params = {"table_name": table, "cold_id": cold_id}

            results = self.db.execute_query(sql, params)

            if not results:
                logger.warning("No record found for table %s with CoLD_ID %s", table, cold_id)
                return {"error": f"No record found for {cold_id} in table {table}"}

            result = results[0]

            # Extract the data from the SQL result
            found_table = result.get("found_table")
            record_id = result.get("record_id")
            complete_record = result.get("complete_record") or {}
            hop1_relations = result.get("hop1_relations") or {}

            # Flatten nested complete_record into top-level (similar to full text search)
            flat_record = {
                "source_table": found_table,
                "id": record_id,
                "cold_id": cold_id,
                "hop1_relations": hop1_relations,
            }

            # Add all fields from complete_record, avoiding id collision
            for key, value in complete_record.items():
                if key == "id":
                    continue
                flat_record[key] = value

            # Apply transformation using the appropriate transformer (similar to full_text_search)
            transformed_record = DataTransformerFactory.transform_result(found_table, flat_record)

            raw_payload = {
                "found_table": found_table,
                "record_id": record_id,
                "complete_record": complete_record,
                "hop1_relations": hop1_relations,
            }

            if response_type == "raw":
                return raw_payload
            if response_type == "both":
                return {"parsed": transformed_record, "raw": raw_payload}
            return transformed_record

        except Exception as e:
            logger.error("Error fetching record %s from table %s: %s", cold_id, table, e)
            return {"error": f"Could not fetch record {cold_id} from table {table}: {str(e)}"}

    def full_table(self, table, response_type: str = "parsed"):
        """
        Fetch all records from a table directly via SQL (data_views.*_complete) and transform.
        """
        try:
            view = self._complete_view_for_table(table)
            sql = f"SELECT c.id AS record_id, to_jsonb(c.*) AS complete_record FROM {view} c"
            rows = self.db.execute_query(sql, {}) or []

            if response_type == "raw":
                return [row.get("complete_record") or {} for row in rows]

            results: list[dict[str, Any]] = []
            for row in rows:
                complete = row.get("complete_record") or {}
                # Flatten: start with metadata, then merge complete_record fields
                flat = {"source_table": table, "id": row.get("record_id")}
                for k, v in complete.items():
                    if k == "id":
                        continue
                    flat[k] = v
                transformed = DataTransformerFactory.transform_result(table, flat)
                if response_type == "both":
                    results.append({"parsed": transformed, "raw": complete})
                else:
                    results.append(transformed)
            return results
        except Exception as e:
            logger.error("Error querying full table %s: %s", table, e)
            return []

    def filtered_table(self, table, filters, response_type: str = "parsed"):
        """
        Fetch and filter records from a table using SQL with mapping-aware filters, then transform.
        """
        try:
            view = self._complete_view_for_table(table)
            alias = "c"
            where_sql, params = self._build_filter_sql(table, alias, filters)
            sql = f"SELECT {alias}.id AS record_id, to_jsonb({alias}.*) AS complete_record FROM {view} {alias}{where_sql}"
            rows = self.db.execute_query(sql, params) or []

            if response_type == "raw":
                return [row.get("complete_record") or {} for row in rows]

            results: list[dict[str, Any]] = []
            for row in rows:
                complete = row.get("complete_record") or {}
                flat = {"source_table": table, "id": row.get("record_id")}
                for k, v in complete.items():
                    if k == "id":
                        continue
                    flat[k] = v
                transformed = DataTransformerFactory.transform_result(table, flat)
                if response_type == "both":
                    results.append({"parsed": transformed, "raw": complete})
                else:
                    results.append(transformed)
            return results
        except Exception as e:
            logger.error(
                "Error querying filtered table %s with filters %s: %s",
                table,
                filters,
                e,
            )
            return []

    """
    =======================================================================
    FULL TEXT SEARCH AND HELPER FUNCTIONS
    =======================================================================
    """

    def _infer_type_from_query(self, search_string: str) -> list[str] | None:
        """
        Infer the type of data the user is looking for based on keywords in the search query.
        Returns a list of table names to prioritize, or None if no inference can be made.
        """
        if not search_string:
            return None

        search_lower = search_string.lower()

        # Keywords to type mappings
        type_keywords = {
            "Domestic Instruments": [
                "legislation",
                "statute",
                "act",
                "law",
                "code",
                "domestic instrument",
                "legal instrument",
            ],
            "Court Decisions": [
                "case",
                "court",
                "decision",
                "judgment",
                "ruling",
                "precedent",
            ],
            "International Instruments": [
                "treaty",
                "convention",
                "international instrument",
                "international agreement",
            ],
            "Regional Instruments": [
                "regional instrument",
                "regional agreement",
                "directive",
                "regulation",
            ],
            "Literature": [
                "article",
                "book",
                "publication",
                "literature",
                "journal",
                "commentary",
            ],
        }

        # Check for matches
        inferred_types = []
        for table_name, keywords in type_keywords.items():
            if any(keyword in search_lower for keyword in keywords):
                inferred_types.append(table_name)

        return inferred_types if inferred_types else None

    def _prioritize_results_by_type(self, rows: list[dict[str, Any]], priority_types: list[str]) -> list[dict[str, Any]]:
        """
        Re-order results to prioritize certain table types while maintaining relative order within each group.
        """
        prioritized = []
        others = []

        for row in rows:
            source_table = row.get("source_table")
            if source_table in priority_types:
                prioritized.append(row)
            else:
                others.append(row)

        # Return prioritized types first, then others
        return prioritized + others

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
        """
        Perform full-text search via data_views.search_all and return correct total_matches
        along with full record data from NocoDB.
        """
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
        # count total matches
        count_sql = (
            "SELECT COUNT(*) AS total_matches FROM data_views.search_all("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(1 AS integer), "
            "page_size := CAST(2147483647 AS integer), "
            "sort_by_date := CAST(:sort_by_date AS boolean)"
            ")"
        )
        count_result = self.db.execute_query(count_sql, params)
        total_matches = count_result[0].get("total_matches", 0) if count_result else 0
        # fetch paginated rows
        logger.debug("Performing full-text search with params: %s", params)
        sql = (
            "SELECT table_name AS source_table, record_id AS id, complete_record AS complete_record, rank, result_date "
            "FROM data_views.search_all("
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
        # log raw SQL rows, serializing dates as strings
        logger.debug("raw SQL results:\n%s", json.dumps(rows, indent=2, default=str))

        # Apply smart type prioritization when not sorting by date
        if not sort_by_date and not tables:
            # Infer type from search query
            inferred_types = self._infer_type_from_query(search_string)

            # Apply prioritization
            if inferred_types:
                # Prioritize inferred types
                logger.debug("Inferred types from query: %s", inferred_types)
                rows = self._prioritize_results_by_type(rows, inferred_types)
            else:
                # Default: prioritize Answers (Questions/Answers) when no type can be inferred
                logger.debug("No type inferred, prioritizing Answers by default")
                rows = self._prioritize_results_by_type(rows, ["Answers", "HCCH Answers"])

        # flatten nested complete_record into top-level
        parsed_results = []
        raw_results = []
        for row in rows:
            complete = row.get("complete_record") or {}
            if response_type in ("parsed", "both"):
                flat = {
                    "source_table": row.get("source_table"),
                    "id": row.get("id"),
                    "rank": row.get("rank"),
                    "result_date": row.get("result_date"),
                }
                for key, value in complete.items():
                    if key == "id":
                        continue
                    flat[key] = value
                # Apply transformation using the appropriate transformer
                table_name = row.get("source_table")
                flat = DataTransformerFactory.transform_result(table_name, flat)
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
                "test": config.TEST,
                "total_matches": total_matches,
                "page": page,
                "page_size": page_size,
                "results": raw_results,
            }
        if response_type == "both":
            combined = [{"parsed": p, "raw": r} for p, r in zip(parsed_results, raw_results, strict=False)]
            return {
                "test": config.TEST,
                "total_matches": total_matches,
                "page": page,
                "page_size": page_size,
                "results": combined,
            }

        return {
            "test": config.TEST,
            "total_matches": total_matches,
            "page": page,
            "page_size": page_size,
            "results": parsed_results,
        }
