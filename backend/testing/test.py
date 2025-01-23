from .database.azure_sql import Database

import os
from dotenv import load_dotenv

load_dotenv()

# PyODBC connection string
connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")


def search_all_tables(search_string):
    # Initialize a dictionary to store the search results
    results = {}
    total_matches = 0  # Initialize a counter for the total number of matches
    search_terms = search_string.split()

    # Connect to the database
    db = Database(connection_string)

    # Get all entries from all tables
    all_entries = db.get_all_entries()

    # Search through all entries
    for table, entries in all_entries.items():
        matching_entries = []
        for entry in entries:
            # Check if any search term is found in any value of the entry
            if any(
                search_term.lower() in str(value).lower()
                for search_term in search_terms
                for value in entry.values()
            ):
                matching_entries.append(entry)

        if matching_entries:
            results[table] = matching_entries
            total_matches += len(matching_entries)

    # Wrap the total matches and all table results into a final JSON response
    final_results = {"total_matches": total_matches, "tables": results}
    return final_results


def main():
    search_string = "yellow submarine"
    results = search_all_tables(search_string)
    print(results)


if __name__ == "__main__":
    main()
