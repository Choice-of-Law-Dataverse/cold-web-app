import json
import numpy as np
from config import Config
from .database import Database
from .embeddings import EmbeddingService
from utils.utils import filter_na, parse_results, flatten_and_transform_data
from utils.sorter import Sorter


class SearchService:
    def __init__(self):
        # self.db = Database(Config.AZURE_POSTGRESQL_DUMMY_CONN_STRING)
        self.db = Database(Config.SQL_CONN_STRING)
        self.test = Config.TEST
        self.sorter = Sorter()

    def curated_details_search(self, table, id):
        print(table)
        print(id)
        if table in [
            "Answers",
            "Legislation",
            "Legal provisions",
            "Court decisions",
            "Jurisdictions",
            "Literature",
        ]:
            final_results = self.db.get_entry_by_id(table, id)
            return filter_na(parse_results(final_results))
        else:
            return filter_na(
                parse_results(
                    {
                        "error": "this table either does not exist or has not been implemented in this route"
                    }
                )
            )

    def full_table(self, table):
        print(table)
        results = self.db.execute_query(f'SELECT * FROM "{table}"')
        return results

    def filtered_table(self, table, filters):
        # Base query
        query = f'SELECT * FROM "{table}"'
        query_params = {}

        # Check if filters are provided and construct WHERE clause
        if filters:
            conditions = []
            for idx, filter_item in enumerate(filters):
                column = filter_item.get("column")
                value = filter_item.get("value")

                if not column or value is None:
                    raise ValueError(f"Invalid filter: {filter_item}")

                # Use LOWER() for case-insensitive matching
                param_key = f"param_{idx}"
                conditions.append(f'LOWER("{column}") = LOWER(:{param_key})')
                query_params[param_key] = value

            # Append the WHERE clause to the query only if there are conditions
            if conditions:
                query += f' WHERE {" AND ".join(conditions)}'

        # Debug: Print the full query and parameters
        print("Executing query:", query)
        print("With parameters:", query_params)

        # Execute the query with parameters as a dictionary
        results = self.db.execute_query(query, query_params)
        return results

    """
    =======================================================================
    FULL TEXT SEARCH AND HELPER FUNCTIONS
    =======================================================================
    """

    def _extract_filters(self, filters):
        tables = []
        jurisdictions = []
        themes = []

        for filter_item in filters:
            column = filter_item.get("column")
            values = filter_item.get("values", [])
            if column and values:
                col_lower = column.lower()
                if col_lower in [
                    "name (from jurisdiction)",
                    "jurisdiction name",
                    "jurisdictions",
                ]:
                    jurisdictions.extend(values)
                elif col_lower in ["themes", "themes name"]:
                    themes.extend(values)
                elif col_lower in ["source_table", "tables"]:
                    tables.extend(values)
        return tables, jurisdictions, themes

    def _build_empty_search_query(self, tables, jurisdictions, themes):
        """Return a UNION of all relevant tables using the same filter structure,
        but *without* the search conditions.*"""

        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        # Notice we do not do ts_rank(...) or search conditions here.
        # Instead, we just select a constant "rank" so we can still ORDER BY (uselessly, but consistent).
        query = f"""
            WITH params AS (
                SELECT
                    {tables_sql}::text[] AS tables,
                    {jurisdictions_sql}::text[] AS jurisdictions,
                    {themes_sql}::text[] AS themes
            )
            -- Answers
            SELECT 
                'Answers' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Answers", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR "Name (from Jurisdiction)" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            -- Court decisions
            SELECT 
                'Court decisions' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Court decisions", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
                    or exists (
                        select 1
                        from unnest(params.jurisdictions) as jurisdiction_filter
                        where "Jurisdiction Names" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            -- Legislation
            SELECT 
                'Legislation' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Legislation", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Legislation' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR "Jurisdiction name" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes name" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            -- Literature
            SELECT 
                'Literature' AS source_table,
                "ID"::text AS id,
                1.0 AS rank
            FROM "Literature", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    array_length(params.themes, 1) is null -- Skip theme filter if empty
                    or exists (
                        select 1
                        from unnest(params.themes) as theme_filter
                        where "Themes" ILIKE '%' || theme_filter || '%'
                    ) -- Case-insensitive partial match for themes
                )

            ORDER BY rank DESC
            LIMIT 150;
        """
        return query

    def _build_fulltext_query(self, search_string, tables, jurisdictions, themes):
        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        query = f"""
            WITH params AS (
                SELECT 
                    {tables_sql}::text[] AS tables,
                    {jurisdictions_sql}::text[] AS jurisdictions,
                    {themes_sql}::text[] AS themes
            )
            -- Search in "Answers" table
            SELECT 
                'Answers' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Answers", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR "Name (from Jurisdiction)" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            -- Search in "Court decisions" table
            SELECT 
                'Court decisions' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Court decisions", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
                    or exists (
                        select 1
                        from unnest(params.jurisdictions) as jurisdiction_filter
                        where "Jurisdiction Names" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            -- Search in "Legislation" table
            SELECT 
                'Legislation' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Legislation", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Legislation' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR "Jurisdiction name" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE "Themes name" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            -- Search in "Literature" table
            SELECT 
                'Literature' AS source_table,
                "ID"::text AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Literature", params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )
                AND (
                    array_length(params.themes, 1) is null -- Skip theme filter if empty
                    or exists (
                        select 1
                        from unnest(params.themes) as theme_filter
                        where "Themes" ILIKE '%' || theme_filter || '%'
                    ) -- Case-insensitive partial match for themes
                )

            -- Combine results and order by rank
            ORDER BY rank DESC
            LIMIT 150;
        """
        return query

    def _to_sql_array(self, values):
        """
        Convert a list of strings to a text[] literal in SQL:
        e.g. ['foo', 'bar'] -> ARRAY['foo','bar']::text[]
        Return None if the list is empty.
        """
        if values:
            return f"ARRAY[{', '.join(repr(v) for v in values)}]::text[]"
        return None

    def full_text_search(self, search_string, filters=[]):
        tables, jurisdictions, themes = self._extract_filters(filters)

        if not search_string or not search_string.strip():
            query = self._build_empty_search_query(tables, jurisdictions, themes)
        else:
            query = self._build_fulltext_query(
                search_string, tables, jurisdictions, themes
            )

        try:
            all_entries = self.db.execute_query(query)
        except Exception as e:
            print(f"Error executing query: {e}")
            return {"test": self.test, "total_matches": 0, "results": []}

        if not all_entries:
            return {"test": self.test, "total_matches": 0, "results": []}

        results = {
            "test": self.test,
            "total_matches": len(all_entries),
            "results": all_entries,
        }

        for index, value in enumerate(results["results"]):
            additional_data = self.db.get_entry_by_id(
                value["source_table"], value["id"]
            )
            if additional_data:
                additional_data.pop("search", None)
                additional_data.pop("Content", None)
                results["results"][index].update(additional_data)

        return filter_na(parse_results(results))
