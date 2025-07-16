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
    
    def list_rows(self, table: str) -> list:
        """
        Fetch all records for a given table from NocoDB via API.
        """
        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/{table}"
        logger.debug("NocoDBService.list_rows: GET %s", url)
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        payload = resp.json()
        # Extract list of records; NocoDB wraps list under 'list' or 'data'
        if isinstance(payload, dict):
            if 'list' in payload and isinstance(payload['list'], list):
                return payload['list']
            if 'data' in payload and isinstance(payload['data'], list):
                return payload['data']
        # If payload itself is a list, return directly
        if isinstance(payload, list):
            return payload
        # Unexpected format, return empty list
        return []
