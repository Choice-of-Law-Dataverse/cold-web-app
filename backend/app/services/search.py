import json
from app.config import config
from app.services.database import Database
from app.services.nocodb import NocoDBService
from app.services.transformers import DataTransformerFactory
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
                # handle lookup/list fields
                if isinstance(cell, list):
                    # string matching in list elements
                    if isinstance(value, str):
                        found = False
                        for elem in cell:
                            if isinstance(elem, dict):
                                for v in elem.values():
                                    if isinstance(v, str) and value.lower() in v.lower():
                                        found = True; break
                                if found: break
                            elif isinstance(elem, str) and value.lower() in elem.lower():
                                found = True; break
                        if not found:
                            match = False; break
                    # numeric or boolean matching in list elements
                    elif isinstance(value, (int, float, bool)):
                        found = False
                        for elem in cell:
                            if elem == value or (isinstance(elem, dict) and elem.get('id') == value):
                                found = True; break
                        if not found:
                            match = False; break
                    else:
                        raise ValueError(f"Unsupported filter type for column {column}: {value}")
                    continue
                # scalar fields
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
        Perform full-text search via data_views.search_all and return correct total_matches
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
            "sort_by_date": sort_by_date,
        }
        # count total matches
        count_sql = (
            "SELECT COUNT(*) AS total_matches FROM data_views.search_all("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(1 AS integer), "
            "page_size := CAST(2147483647 AS integer), "
            "sort_by_date := CAST(:sort_by_date AS boolean)"
            ")"
        )
        count_result = self.db.execute_query(count_sql, params)
        total_matches = count_result[0].get("total_matches", 0) if count_result else 0
        # fetch paginated rows
        print(f"Performing full-text search with params: {params}")
        sql = (
            "SELECT table_name AS source_table, record_id AS id, complete_record AS complete_record, rank, result_date "
            "FROM data_views.search_all("
            "search_term := CAST(:search_term AS text), "
            "filter_tables := CAST(:filter_tables AS text[]), "
            "filter_jurisdictions := CAST(:filter_jurisdictions AS text[]), "
            "filter_themes := CAST(:filter_themes AS text[]), "
            "page := CAST(:page AS integer), "
            "page_size := CAST(:page_size AS integer), "
            "sort_by_date := CAST(:sort_by_date AS boolean)"
            ")"
        )
        rows = self.db.execute_query(sql, params)
        # print raw SQL rows, serializing dates as strings
        print("raw SQL results:\n", json.dumps(rows, indent=2, default=str))
        # flatten nested complete_record into top-level
        flattened = []
        for row in rows:
            complete = row.get("complete_record") or {}
            flat = {
                "source_table": row.get("source_table"),
                "id": row.get("id"),
                "rank": row.get("rank"),
                "result_date": row.get("result_date"),
            }
            for key, value in complete.items():
                if key == "id":
                    continue
                flat[key] = value
            
            # Apply transformation using the appropriate transformer
            table_name = row.get("source_table")
            flat = DataTransformerFactory.transform_result(table_name, flat)
            
            flattened.append(flat)
        
        return {
            "test": config.TEST,
            "total_matches": total_matches,
            "page": page,
            "page_size": page_size,
            "results": flattened,
        }