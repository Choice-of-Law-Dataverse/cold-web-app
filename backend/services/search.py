import numpy as np
from config import Config
from .database import Database
from .embeddings import EmbeddingService
from utils.utils import filter_na, parse_results, sort_by_similarity, flatten_and_transform_data

class SearchService:
    def __init__(self):
        self.db = Database(Config.AZURE_SQL_CONNECTION_STRING)

    def basic_search(self, search_string):
        all_entries = self.db.get_all_entries()
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
            'total_matches': total_matches,
            'tables': results
            }
        return filter_na(parse_results(final_results))

    def filtered_search(self, search_string, filter_string):
        return "foo"

    def semantic_search(self, search_string):
        return "foo"