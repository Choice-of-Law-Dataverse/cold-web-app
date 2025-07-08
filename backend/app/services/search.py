import json
from app.config import config
from app.services.database import Database
from app.services.nocodb import NocoDBService
import logging

# logger for this module
logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        self.test = config.TEST
        # initialize NocoDB service for data augmentation
        self.nocodb = NocoDBService(
            base_url=config.NOCODB_BASE_URL,
            api_token=config.NOCODB_API_TOKEN,
        )

    def curated_details_search(self, table, id):
        """
        Fetch a single record by table and id using the new database function.
        """
        result = self.db.execute_query(
            "SELECT cold_views.curated_details_search(:table_name, :record_id) AS data",
            {"table_name": table, "record_id": id},
        )
        if result:
            data = result[0].get("data")
            if isinstance(data, str):
                data = json.loads(data)
            return data
        return {"error": "no entry found with the specified id"}

    def full_table(self, table):
        """
        Fetch all records from a table using the new database function.
        """
        rows = self.db.execute_query(
            "SELECT t.data FROM cold_views.full_table(:table_name) AS t(data)",
            {"table_name": table},
        )
        results = []
        for row in rows:
            val = row.get("data")
            if isinstance(val, str):
                results.append(json.loads(val))
            else:
                results.append(val)
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

    def full_text_search(self, search_string, filters=[], page=1, page_size=50, sort_by_date=False):
        """
        Perform full-text search via cold_views.search_all and return correct total_matches
        along with full record data from NocoDB.
        """
        tables, jurisdictions, themes = self._extract_filters(filters)
        params = {
            "search_term": search_string,
            "filter_tables": tables or None,
            "filter_jurisdictions": jurisdictions or None,
            "filter_themes": themes or None,
            "page": page,
            "page_size": page_size,
        }
        # count total matches
        count_sql = (
            "SELECT COUNT(*) AS total_matches FROM cold_views.search_all("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(1 AS integer), "
            "page_size := CAST(2147483647 AS integer)"
            ")"
        )
        count_result = self.db.execute_query(count_sql, params)
        total_matches = count_result[0].get("total_matches", 0) if count_result else 0
        # fetch paginated rows
        print(f"Performing full-text search with params: {params}")
        sql = (
            "SELECT table_name AS source_table, record_id AS id, title, excerpt, rank "
            "FROM cold_views.search_all("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(:page AS integer), "
            "page_size := CAST(:page_size AS integer)"
            ")"
        )
        rows = self.db.execute_query(sql, params)
        print("raw SQL results:\n", json.dumps(rows, indent=2))
        # augment each row with full NocoDB data
        augmented = []
        for row in rows:
            table = row.get("source_table")
            record_id = row.get("id")
            try:
                full_data = self.nocodb.get_row(table, record_id)
            except Exception:
                full_data = {}
            # Always include NocoDB enrichment under a dedicated key
            merged = {**row, **full_data}
            merged["nocodb_data"] = full_data  # Add enrichment explicitly
            augmented.append(merged)
        return {
            "test": config.TEST,
            "total_matches": total_matches,
            "page": page,
            "page_size": page_size,
            "results": augmented,
        }