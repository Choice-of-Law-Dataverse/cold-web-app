import json
import numpy as np
from config import Config
from .database import Database
from .embeddings import EmbeddingService
from utils.utils import filter_na, parse_results, flatten_and_transform_data
from utils.sorter import Sorter

class SearchService:
    def __init__(self):
        #self.db = Database(Config.AZURE_POSTGRESQL_DUMMY_CONN_STRING)
        self.db = Database(Config.SQL_CONN_STRING)
        self.test = Config.TEST
        self.sorter = Sorter()

    def basic_search(self, search_string):
        all_entries = self.db.get_all_entries()

        # Check if the database retrieval failed without an exception
        if all_entries is None:
            return json.dumps({
                f"{self.test}_error": "Failed to retrieve data from the database. Please try again later."
            })

        results = {}
        total_matches = 0
        search_terms = search_string.lower().split()

        for table, entries in all_entries.items():
            matching_entries = [
                entry for entry in entries
                if all(any(search_term in str(value).lower() for value in entry.values()) for search_term in search_terms)
            ]
            if matching_entries:
                results[table] = {
                    'matches': len(matching_entries),
                    'results': matching_entries
                }
                total_matches += len(matching_entries)

        final_results = {
            'test': self.test,
            'total_matches': total_matches,
            'tables': results
            }
        # Sort data based on "Case rank" and completeness
        sorted_results = self.sorter.sort_by_priority_and_completeness(final_results)

        return filter_na(parse_results(sorted_results))

    def filtered_search(self, search_string, filter_string):
        return f"{self.test}...foo"

    def semantic_search(self, search_string):
        return f"{self.test}...foo"

    def curated_search(self, search_string):
        all_entries = self.db.get_entries_from_tables(['Answers', 'Court decisions'])

        # Check if the database retrieval failed without an exception
        if all_entries is None:
            return json.dumps({
                f"{self.test}_error": "Failed to retrieve data from the database. Please try again later."
            })

        # Pre-selection of columns for each table
        selected_columns = {
            'Answers': [
                'ID', 'Name (from Jurisdiction)', 'Questions', 'Answer', 'More information', 
                'Legal provision articles', 'Secondary legal provision articles', 
                'Legislation titles', 'Case titles'
            ],
            'Court decisions': [
                'ID', 'Case', 'Jurisdiction Names', 'Abstract', 'Content', 
                'Additional information', 'Themes', 'Observations', 'Relevant facts / Summary of the case', 
                'Relevant rules of law involved', 'Choice of law issue', 'Court\'s position', 
                'Text of the relevant legal provisions', 'Quote', 'Translated excerpt', 
                'Case rank', 'Pinpoint facts', 'Pinpoint rules', 'Pinpoint CoL', 'Answer IDs'
            ]
        }

        results = {}
        total_matches = 0
        search_terms = search_string.lower().split()

        for table, entries in all_entries.items():
            # Filter out only the relevant columns
            filtered_entries = [
                {key: entry[key] for key in selected_columns[table] if key in entry}
                for entry in entries
            ]

            matching_entries = [
                entry for entry in filtered_entries
                if all(any(search_term in str(value).lower() for value in entry.values()) for search_term in search_terms)
            ]
            if matching_entries:
                results[table] = {
                    'matches': len(matching_entries),
                    'results': matching_entries
                }
                total_matches += len(matching_entries)
        
        #print(results)

        final_results = {
            'test': self.test,
            'total_matches': total_matches,
            'tables': results#sort_by_priority_and_completeness(results) # Sort data based on "Case rank" and completeness
            }

        return self.sorter.sorting_chain(filter_na(parse_results(final_results)))

    def curated_details_search(self, table, id):
        print(table)
        print(id)
        if table in ['Answers', 'Legislation', 'Legal provisions', 'Court decisions', 'Jurisdictions']:
            final_results = self.db.get_entry_by_id(table, id)
            return filter_na(parse_results(final_results))
        else:
            return filter_na(parse_results({"error": "this table either does not exist or has not been implemented in this route"}))
    
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
                column = filter_item.get('column')
                value = filter_item.get('value')

                if not column or value is None:
                    raise ValueError(f"Invalid filter: {filter_item}")

                # Use LOWER() for case-insensitive matching
                param_key = f'param_{idx}'
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
        
    def full_text_search(self, search_string, filters=[]):
        # Initialize filter arrays for params
        tables = []
        jurisdictions = []
        themes = []

        # Process filters into appropriate arrays
        for filter_item in filters:
            column = filter_item.get('column')
            values = filter_item.get('values', [])
            if column and values:
                if column.lower() in ['name (from jurisdiction)', 'jurisdiction name']:
                    jurisdictions.extend(values)
                elif column.lower() in ['themes', 'themes name']:
                    themes.extend(values)
                elif column.lower() in ['source_table', 'tables']:
                    tables.extend(values)

        # Convert filter arrays to SQL-compatible lists
        def to_sql_array(values):
            return f"ARRAY[{', '.join(f'\'{v.replace('\'', '\'\'')}\'' for v in values)}]::text[]" if values else "NULL"

        tables_sql = to_sql_array(tables)
        jurisdictions_sql = to_sql_array(jurisdictions)
        themes_sql = to_sql_array(themes)

        # Define the dynamic SQL query
        query = f"""
            WITH params AS (
                SELECT 
                    {tables_sql} AS tables,
                    {jurisdictions_sql} AS jurisdictions,
                    {themes_sql} AS themes
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
                    array_length(params.jurisdictions, 1) IS NULL 
                    OR "Jurisdiction Names" = ANY(params.jurisdictions)
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

            -- Combine results and order by rank
            ORDER BY rank DESC
            LIMIT 150;
        """

        # Debug: Print the final query
        print("Executing Query:", query)

        # Execute the query
        try:
            all_entries = self.db.execute_query(query)
        except Exception as e:
            print(f"Error executing query: {e}")
            return {
                "test": self.test,
                "total_matches": 0,
                "results": []
            }

        # Check if any results were returned
        if not all_entries:
            return {
                "test": self.test,
                "total_matches": 0,
                "results": []
            }

        # Parse results
        results = {
            "test": self.test,
            "total_matches": len(all_entries),
            "results": all_entries
        }

        return filter_na(parse_results(results))
