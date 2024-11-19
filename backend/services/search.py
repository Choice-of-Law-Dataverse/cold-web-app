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
        
    def full_text_search(self, search_string):
        # Prepare the SQL query with dynamic search string input
        query = f"""
            -- COMBINED SEARCH

            -- Search in "Answers", "Court decisions", and "Legislation" tables with the same query

            -- Search in "Answers" table
            select 
            'Answers' as source_table,               -- Column to indicate the source table
            "ID" as id,
            ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
            ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) as rank
            from "Answers"
            where search @@ websearch_to_tsquery('english', '{search_string}')
            or search @@ websearch_to_tsquery('simple', '{search_string}')

            union all

            -- Search in "Court decisions" table
            select 
            'Court decisions' as source_table,       -- Indicate the source table
            "ID" as id,
            ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
            ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) as rank
            from "Court decisions"
            where search @@ websearch_to_tsquery('english', 'arbitral tribunal')
            or search @@ websearch_to_tsquery('simple', 'arbitral tribunal')

            union all

            -- Search in "Court decisions" table
            select 
            'Legislation' as source_table,       -- Indicate the source table
            "ID" as id,
            ts_rank(search, websearch_to_tsquery('english', 'arbitral tribunal')) +
            ts_rank(search, websearch_to_tsquery('simple', 'arbitral tribunal')) as rank
            from "Legislation"
            where search @@ websearch_to_tsquery('english', '{search_string}')
            or search @@ websearch_to_tsquery('simple', '{search_string}')

            -- Combine results and order by rank
            order by rank desc
            limit 250;
        """

        # Execute the SQL query
        all_entries = self.db.execute_query(query)

        # Check if the query returned any results
        if not all_entries:
            empty = {
                "test": self.test,
                "total_matches": 0,
                "results": []
            }
            return empty

        # Parse the results into the desired format
        results = {
            "test": self.test,
            "total_matches": len(all_entries),
            "results": all_entries  # Combine all results into one list
        }

        # Augment the results with the additional columns from the respective tables
        for index, value in enumerate(results['results']):
            # Fetch additional data from the source table
            additional_data = self.db.get_entry_by_id(value['source_table'], value['id'])
            if additional_data:
                # remove unwanted columns
                additional_data.pop('search', None)
                additional_data.pop('Content', None)
                # Merge additional data into the result (update the specific entry in the list)
                results['results'][index].update(additional_data)

        # Return parsed results
        return filter_na(parse_results(results))
