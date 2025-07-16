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
        Fetch a single record by table and id using the NocoDB API.
        """
        try:
            data = self.nocodb.get_row(table, id)
            return data
        except Exception as e:
            logger.error("Error fetching record %s from table %s: %s", id, table, e)
            return {"error": f"Could not fetch record {id} from table {table}"}

    def full_table(self, table):
        """
        Fetch all records from a table using the NocoDB API.
        """
        try:
            data = self.nocodb.list_rows(table)
            return data
        except Exception as e:
            logger.error("Error listing records from table %s: %s", table, e)
            return []

    def filtered_table(self, table, filters):
        """
        Fetch and filter records from a table using the NocoDB API.
        """
        try:
            rows = self.nocodb.list_rows(table)
        except Exception as e:
            logger.error("Error listing records from table %s: %s", table, e)
            return []
        if not filters:
            return rows
        results = []
        for raw in rows:
            # ensure each row is a dict; parse JSON strings if necessary
            if isinstance(raw, str):
                try:
                    row = json.loads(raw)
                except Exception:
                    continue
            elif isinstance(raw, dict):
                row = raw
            else:
                continue
            match = True
            for filter_item in filters:
                column = filter_item.column
                value = filter_item.value
                cell = row.get(column)
                if cell is None:
                    match = False
                    break
                if isinstance(value, str):
                    if not isinstance(cell, str) or value.lower() not in cell.lower():
                        match = False
                        break
                elif isinstance(value, (int, float, bool)):
                    if cell != value:
                        match = False
                        break
                else:
                    raise ValueError(f"Unsupported filter type for column {column}: {value}")
            if match:
                results.append(row)
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
            print("Full data from NocoDB for row:", full_data)
            merged = {**row, **full_data}
            merged["nocodb_data"] = full_data  # Add enrichment explicitly
            # merge all full_data fields into top-level, unwrap lists
            for k, v in full_data.items():
                if isinstance(v, list):
                    # unwrap list of dicts or join primitive lists
                    if v and isinstance(v[0], dict):
                        merged[k] = v[0]
                    else:
                        merged[k] = ", ".join(str(x) for x in v)
                else:
                    merged[k] = v
            augmented.append(merged)
        return {
            "test": config.TEST,
            "total_matches": total_matches,
            "page": page,
            "page_size": page_size,
            "results": augmented,
        }