import requests
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
        url = f"{self.base_url}/api/v1/db/data/{table}/{record_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        payload = resp.json()
        # NocoDB returns data under 'data' key
        return payload.get('data', {})
