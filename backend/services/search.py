import numpy as np
from scipy.spatial.distance import cosine
from config import Config
from .database import Database
from .embeddings import EmbeddingService
from utils.utils import filter_na, parse_results, sort_by_similarity, flatten_and_transform_data

class SearchService:
    def __init__(self):
        self.db = Database(Config.AZURE_SQL_CONNECTION_STRING)

    def basic_search(self, search_string):
        all_entries = self.db.get_all_entries()
        results, total_matches = {}, 0

        for table, entries in all_entries.items():
            matching_entries = [entry for entry in entries if any(search_term.lower() in str(value).lower() for search_term in search_string.split() for value in entry.values())]
            if matching_entries:
                results[table] = matching_entries
                total_matches += len(matching_entries)

        final_results = {'total_matches': total_matches, 'tables': results}
        return filter_na(parse_results(final_results))
