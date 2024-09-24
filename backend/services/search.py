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
        if table == 'Legal provisions' or table == 'Court decisions':
            final_results = self.db.get_entry_by_id(table, id)
            return filter_na(parse_results(final_results))
            """
            SELECT *
            FROM "Legal provisions"
            WHERE "Name" = 'Swi-148 Art. 117';
            "table": "Legal provisions",
            "id": "Swi-148 Art. 117"
            """
        else:
            return filter_na(parse_results({"error": "this table does not exist or if you are sure it does please ask Simon to implement the detailed search for this table"}))
            """
            SELECT *
            FROM "Court decisions"
            WHERE "ID" = 'CHE-1017';
            "table": "Court decisions",
            "id": "CHE-1017"
            """
        