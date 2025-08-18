import requests
import logging
from app.config import config

class NocoDBService:
    def __init__(self, base_url: str, api_token: str = None):
        if not base_url:
            raise ValueError("NocoDB base URL not configured")
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        if api_token:
            # X nocodb API token header
            self.headers['xc-token'] = api_token

    def get_row(self, table: str, record_id: str) -> dict:
        """
        Fetch full record data and metadata for a specific row from NocoDB.
        """
        print(f"Fetching row {record_id} from table {table} in NocoDB")
        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/{table}/{record_id}"
        logger.debug("NocoDBService.get_row: GET %s", url)
        logger.debug("NocoDBService headers: %s", self.headers)
        resp = requests.get(url, headers=self.headers)
        print("Response from nocoDB:", resp.status_code, resp.text)
        resp.raise_for_status()
        payload = resp.json()
        logger.debug("NocoDBService.get_row response payload: %s", payload)
        # return full payload directly
        return payload
    
    def list_rows(self, table: str, filters: list = None, limit: int = 100) -> list:
        """
        Fetch records for a given table via NocoDB API, applying optional filters and paging through all pages.
        """
        logger = logging.getLogger(__name__)
        records = []
        offset = 0
        # build where parameter if filters provided
        where_clauses = []
        if filters:
            for f in filters:
                col = f.column
                val = f.value
                # choose operator
                op = 'ct' if isinstance(val, str) else 'eq'
                # escape comma or parentheses in val?
                where_clauses.append(f"({col},{op},{val})")
        where_param = '~and'.join(where_clauses) if where_clauses else None
        while True:
            url = f"{self.base_url}/{table}"
            params = {'limit': limit, 'offset': offset}
            if where_param:
                params['where'] = where_param
            logger.debug("NocoDBService.list_rows: GET %s with params %s", url, params)
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            payload = resp.json()
            # extract batch results
            if isinstance(payload, dict):
                batch = payload.get('list') or payload.get('data') or []
                # check pageInfo for last page
                page_info = payload.get('pageInfo', {})
                is_last = page_info.get('isLastPage', False)
            elif isinstance(payload, list):
                batch = payload
                is_last = True
            else:
                break
            if not batch:
                break
            records.extend(batch)
            if is_last or len(batch) < limit:
                break
            offset += limit
        return records
