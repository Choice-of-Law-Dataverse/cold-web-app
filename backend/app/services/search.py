import json
import numpy as np
from app.config import config
from app.services.database import Database
from app.services.utils import filter_na, parse_results, deduplicate_entries


class SearchService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.test = config.TEST

    def curated_details_search(self, table, id):
        print(table)
        print(id)
        if table in [
            "Answers",
            "Domestic Instruments",
            "Domestic Legal Provisions",
            "Regional Instruments",
            "Regional Legal Provisions",
            "International Instruments",
            "International Legal Provisions",
            "Court Decisions",
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
                column = filter_item.column
                value = filter_item.value

                if not column or value is None:
                    raise ValueError(f"Invalid filter: {filter_item}")

                param_key = f"param_{idx}"

                # Determine the type of the filter value and choose the operator accordingly
                if isinstance(value, str):
                    # Use ILIKE for case-insensitive partial matching
                    conditions.append(f'"{column}" ILIKE :{param_key}')
                    query_params[param_key] = f"%{value}%"
                elif isinstance(value, (int, float, bool)):
                    # Use equality operator for integers, floats, and booleans
                    conditions.append(f'"{column}" = :{param_key}')
                    query_params[param_key] = value
                else:
                    # If you want to support other types later, add them here.
                    raise ValueError(
                        f"Unsupported filter type for column {column}: {value}"
                    )

            # Append the WHERE clause to the query if conditions exist
            if conditions:
                query += f' WHERE {" AND ".join(conditions)}'

        # Debug: Print the full query and parameters
        # print("Executing query:", query)
        # print("With parameters:", query_params)

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
            column = filter_item.column
            raw_values = filter_item.values
            values = (
                raw_values
                if isinstance(raw_values, list)
                else [raw_values] if raw_values is not None else []
            )

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

    def _to_sql_array(self, values):
        """Convert a list of strings to a text[] literal in SQL."""
        if values:
            return f"ARRAY[{', '.join(repr(v) for v in values)}]::text[]"
        return None

    def _build_empty_search_query(self, tables, jurisdictions, themes):
        """
        Return all rows (union across all relevant tables) using the same filter logic,
        but no search conditions. We'll keep 'rank' = 1.0 as a dummy field.
        Then do ORDER BY rank DESC, and apply OFFSET/LIMIT later.
        """
        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        union_part = f"""
            SELECT 
                'Answers' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Answers" AS ans, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR ans."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE ans."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            -- HCCH Answers

            SELECT 
                'HCCH Answers' AS source_table,
                "ID"::text AS id,
                1.0 AS rank
            FROM "HCCH Answers" AS hc, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'HCCH Answers' = ANY(params.tables))
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE hc."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            SELECT 
                'Court Decisions' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Court Decisions" AS cd, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court Decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE cd."Jurisdictions" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE cd."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            SELECT 
                'Domestic Instruments' AS source_table,
                "ID" AS id,
                1.0 AS rank
            FROM "Domestic Instruments" AS di, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Domestic Instruments' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR di."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL
                )

            UNION ALL

            -- International Legal Provisions
            --SELECT 
                --'International Legal Provisions' AS source_table,
                --"ID" AS id,
                --1.0 AS rank
            --FROM "International Legal Provisions" AS ilp, params
            --WHERE 
                --(array_length(params.tables, 1) IS NULL OR 'International Legal Provisions' = ANY(params.tables))
                --AND (
                    --array_length(params.jurisdictions, 1) IS NULL 
                    --OR ilp."Instrument" = ANY(params.jurisdictions)
                --)

            --UNION ALL

            SELECT 
                'Literature' AS source_table,
                "ID"::text AS id,
                1.0 AS rank
            FROM "Literature" AS lit, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE lit."Jurisdiction" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE lit."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            ORDER BY rank DESC
        """

        query = f"""
        WITH params AS (
            SELECT
                {tables_sql}::text[] AS tables,
                {jurisdictions_sql}::text[] AS jurisdictions,
                {themes_sql}::text[] AS themes
        ),
        full_results AS (
            {union_part}
        )
        SELECT *
        FROM full_results
        OFFSET :offset
        LIMIT :limit;
        """
        return query

    # ----------------------------------------------------------------------
    # Queries for "search string provided" scenario (full-text).
    # ----------------------------------------------------------------------

    def _build_empty_search_count_query(self, tables, jurisdictions, themes):
        """
        Same union logic as _build_empty_search_query, but returns a COUNT(*).
        """
        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        # Instead of SELECT source_table, ID, 1.0, we do SELECT 1
        # and skip ORDER BY, OFFSET, LIMIT
        union_part = f"""
            SELECT 1
            FROM "Answers" AS ans, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR ans."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE ans."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            SELECT 1
            FROM "HCCH Answers" AS hc, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'HCCH Answers' = ANY(params.tables))
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE hc."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            SELECT 1
            FROM "Court Decisions" AS cd, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court Decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE cd."Jurisdictions" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE cd."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )

            UNION ALL

            SELECT 1
            FROM "Domestic Instruments" AS di, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Domestic Instruments' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR di."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL
                )

            UNION ALL

            --SELECT 1
            --FROM "International Legal Provisions" AS ilp, params
            --WHERE 
                --(array_length(params.tables, 1) IS NULL OR 'International Legal Provisions' = ANY(params.tables))
                --AND (
                    --array_length(params.jurisdictions, 1) IS NULL 
                    --OR ilp."Instrument" = ANY(params.jurisdictions)
                --)

            --UNION ALL

            SELECT 1
            FROM "Literature" AS lit, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE lit."Jurisdiction" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE lit."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
        """

        query = f"""
        WITH params AS (
            SELECT
                {tables_sql}::text[] AS tables,
                {jurisdictions_sql}::text[] AS jurisdictions,
                {themes_sql}::text[] AS themes
        ),
        full_results AS (
            {union_part}
        )
        SELECT COUNT(*) AS total_count
        FROM full_results;
        """

        return query

    def _build_fulltext_query(self, search_string, tables, jurisdictions, themes):
        """
        Union of all tables with search conditions,
        plus an ORDER BY rank, but no LIMIT. We'll do offset/limit at the end.
        """
        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        union_part = f"""
            SELECT 
                'Answers' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Answers" AS ans, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR ans."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE ans."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL


            -- Search in "HCCH Answers" table

            SELECT 
                'HCCH Answers' AS source_table,
                "ID"::text AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "HCCH Answers" AS hc, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'HCCH Answers' = ANY(params.tables))
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE hc."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            SELECT 
                'Court Decisions' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Court Decisions" AS cd, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court Decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE cd."Jurisdictions" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE cd."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            SELECT 
                'Domestic Instruments' AS source_table,
                "ID" AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Domestic Instruments" AS di, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Domestic Instruments' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR di."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            -- Search in "International Legal Provisions" table
            --SELECT 
                --'International Legal Provisions' AS source_table,
                --"ID" AS id,
                --ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                --ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            --FROM "International Legal Provisions" AS ilp, params
            --WHERE 
                --(array_length(params.tables, 1) IS NULL OR 'International Legal Provisions' = ANY(params.tables))
                --AND (
                    --array_length(params.jurisdictions, 1) IS NULL 
                    --OR ilp."Instrument" = ANY(params.jurisdictions)
                --)
                --AND (
                    --search @@ websearch_to_tsquery('english', '{search_string}')
                    --OR search @@ websearch_to_tsquery('simple', '{search_string}')
                --)

            --UNION ALL

            SELECT 
                'Literature' AS source_table,
                "ID"::text AS id,
                ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
                ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) AS rank
            FROM "Literature" AS lit, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE lit."Jurisdiction" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE lit."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            ORDER BY rank DESC
        """

        # Wrap in a CTE, then OFFSET/LIMIT at the end:
        query = f"""
        WITH params AS (
            SELECT
                {tables_sql}::text[] AS tables,
                {jurisdictions_sql}::text[] AS jurisdictions,
                {themes_sql}::text[] AS themes
        ),
        full_results AS (
            {union_part}
        )
        SELECT *
        FROM full_results
        OFFSET :offset
        LIMIT :limit;
        """
        return query

    def _build_fulltext_count_query(self, search_string, tables, jurisdictions, themes):
        """
        Same union as _build_fulltext_query, but we select only for counting.
        """
        tables_sql = self._to_sql_array(tables) or "NULL"
        jurisdictions_sql = self._to_sql_array(jurisdictions) or "NULL"
        themes_sql = self._to_sql_array(themes) or "NULL"

        union_part = f"""
            SELECT 1
            FROM "Answers" AS ans, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Answers' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR ans."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE ans."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            SELECT 1
            FROM "HCCH Answers" AS hc, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'HCCH Answers' = ANY(params.tables))
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE hc."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            SELECT 1
            FROM "Court Decisions" AS cd, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Court Decisions' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE cd."Jurisdictions" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) IS NULL 
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE cd."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            SELECT 1
            FROM "Domestic Instruments" AS di, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Domestic Instruments' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR di."Jurisdictions" = ANY(params.jurisdictions)
                )
                AND (
                    array_length(params.themes, 1) IS NULL
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )

            UNION ALL

            --SELECT 1
            --FROM "International Legal Provisions" AS ilp, params
            --WHERE 
                --(array_length(params.tables, 1) IS NULL OR 'International Legal Provisions' = ANY(params.tables))
                --AND (
                    --array_length(params.jurisdictions, 1) IS NULL 
                    --OR ilp."Instrument" = ANY(params.jurisdictions)
                --)
                --AND (
                    --search @@ websearch_to_tsquery('english', '{search_string}')
                    --OR search @@ websearch_to_tsquery('simple', '{search_string}')
                --)

            --UNION ALL

            SELECT 1
            FROM "Literature" AS lit, params
            WHERE 
                (array_length(params.tables, 1) IS NULL OR 'Literature' = ANY(params.tables))
                AND (
                    array_length(params.jurisdictions, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.jurisdictions) AS jurisdiction_filter
                        WHERE lit."Jurisdiction" ILIKE '%' || jurisdiction_filter || '%'
                    )
                )
                AND (
                    array_length(params.themes, 1) is null
                    OR EXISTS (
                        SELECT 1
                        FROM unnest(params.themes) AS theme_filter
                        WHERE lit."Themes" ILIKE '%' || theme_filter || '%'
                    )
                )
                AND (
                    search @@ websearch_to_tsquery('english', '{search_string}')
                    OR search @@ websearch_to_tsquery('simple', '{search_string}')
                )
        """

        query = f"""
        WITH params AS (
            SELECT
                {tables_sql}::text[] AS tables,
                {jurisdictions_sql}::text[] AS jurisdictions,
                {themes_sql}::text[] AS themes
        ),
        full_results AS (
            {union_part}
        )
        SELECT COUNT(*) AS total_count
        FROM full_results;
        """
        return query

    def full_text_search(self, search_string, filters=[], page=1, page_size=50):
        """
        Perform a full-text search with optional filters, returning one 'page' of results.
        page_size is how many rows per page, page is which page number (1-based).
        """

        # Extract filter-specific lists
        tables, jurisdictions, themes = self._extract_filters(filters)

        # If there's no search term, we do the "empty" version (just the filter).
        if not search_string or not search_string.strip():
            base_query = self._build_empty_search_query(tables, jurisdictions, themes)
            count_query = self._build_empty_search_count_query(tables, jurisdictions, themes)
        else:
            base_query = self._build_fulltext_query(search_string, tables, jurisdictions, themes)
            count_query = self._build_fulltext_count_query(search_string, tables, jurisdictions, themes)

        offset_val = max(page - 1, 0) * page_size  # convert page to 0-based offset

        # 1) Get total count
        try:
            total_rows_result = self.db.execute_query(count_query)
            total_count = total_rows_result[0]["total_count"] if total_rows_result else 0
        except Exception as e:
            print(f"Count query error: {e}")
            return {"test": self.test, "total_matches": 0, "page": page, "page_size": page_size, "results": []}

        # 2) Get paginated items
        try:
            all_entries = self.db.execute_query(
                base_query,
                {"offset": offset_val, "limit": page_size}
            )
        except Exception as e:
            print(f"Search query error: {e}")
            return {"test": self.test, "total_matches": 0, "page": page, "page_size": page_size, "results": []}

        if not all_entries:
            return {
                "test": self.test,
                "total_matches": 0,
                "page": page,
                "page_size": page_size,
                "results": []
            }

        # Deduplicate
        deduped_entries = deduplicate_entries(all_entries)

        # Fetch additional data for each result
        for index, value in enumerate(deduped_entries):
            additional_data = self.db.get_entry_by_id(value["source_table"], value["id"])
            if additional_data:
                additional_data.pop("search", None)
                additional_data.pop("Content", None)
                deduped_entries[index].update(additional_data)

        final_results = filter_na(parse_results(deduped_entries))

        return {
            "test": self.test,
            "total_matches": total_count,
            "page": page,
            "page_size": page_size,
            "results": final_results
        }