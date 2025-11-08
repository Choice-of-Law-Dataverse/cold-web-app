import logging
from collections.abc import Sequence
from typing import Any

from app.services.http_session_manager import http_session_manager

logger = logging.getLogger(__name__)


class NocoDBService:
    def __init__(self, base_url: str, api_token: str | None = None):
        if not base_url:
            raise ValueError("NocoDB base URL not configured")
        self.base_url = base_url.rstrip("/")
        self.headers: dict[str, str] = {}
        if api_token:
            # X nocodb API token header
            self.headers["xc-token"] = api_token
        # Use singleton HTTP session manager for connection pooling
        self.session = http_session_manager.get_session()

    def get_row(self, table: str, record_id: str) -> dict[str, Any]:
        """
        Fetch full record data and metadata for a specific row from NocoDB.
        """
        logger.debug("Fetching row %s from table %s in NocoDB", record_id.strip(), table.strip())
        url = f"{self.base_url}/{table}/{record_id}"
        logger.debug("NocoDBService.get_row: GET %s", url)
        logger.debug("NocoDBService headers: %s", self.headers)
        resp = self.session.get(url, headers=self.headers)
        logger.debug("Response from nocoDB: %s %s", resp.status_code, resp.text.strip())
        resp.raise_for_status()
        payload = resp.json()
        logger.debug("NocoDBService.get_row response payload: %s", payload)
        # return full payload directly
        return payload

    def list_rows(
        self,
        table: str,
        filters: Sequence[Any] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Fetch records for a given table via NocoDB API, applying optional filters and paging through all pages.
        """
        records: list[dict[str, Any]] = []
        offset = 0
        # build where parameter if filters provided
        where_clauses: list[str] = []
        if filters:
            for f in filters:
                col = getattr(f, "column", None)
                val = getattr(f, "value", None)
                # choose operator
                op = "ct" if isinstance(val, str) else "eq"
                # escape comma or parentheses in val?
                if col is not None and val is not None:
                    where_clauses.append(f"({col},{op},{val})")
        where_param = "~and".join(where_clauses) if where_clauses else None
        while True:
            url = f"{self.base_url}/{table}"
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if where_param:
                params["where"] = where_param
            logger.debug("NocoDBService.list_rows: GET %s with params %s", url, params)
            resp = self.session.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            payload = resp.json()
            # extract batch results
            if isinstance(payload, dict):
                batch_raw = payload.get("list") or payload.get("data") or []
                batch = batch_raw if isinstance(batch_raw, list) else []
                # check pageInfo for last page
                page_info = payload.get("pageInfo", {})
                is_last = page_info.get("isLastPage", False)
            elif isinstance(payload, list):
                batch = payload
                is_last = True
            else:
                break
            if not batch:
                break
            records.extend([entry for entry in batch if isinstance(entry, dict)])
            if is_last or len(batch) < limit:
                break
            offset += limit
        return records
