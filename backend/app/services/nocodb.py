import logging
from collections.abc import Sequence
from io import BytesIO
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

    def create_row(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new record in NocoDB via API.
        Returns the created record with its ID and metadata.
        """
        logger.debug("Creating row in table %s with data: %s", table, data)
        url = f"{self.base_url}/{table}"
        resp = self.session.post(url, headers=self.headers, json=data)
        logger.debug("Create row response: %s %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        result = resp.json()
        logger.debug("Created row result: %s", result)
        return result

    def upload_file(
        self,
        table: str,
        record_id: int,
        column_name: str,
        file_data: bytes,
        filename: str,
        mime_type: str = "application/pdf",
    ) -> dict[str, Any]:
        """
        Upload a file to a NocoDB attachment field.
        According to NocoDB docs, files should be uploaded using multipart/form-data.

        Reference: https://nocodb.com/docs/product-docs/developer-resources/rest-apis/upload-via-api#python
        """
        logger.debug(
            "Uploading file to table %s, record %s, column %s, filename %s",
            table,
            record_id,
            column_name,
            filename,
        )
        # Step 1: Upload file to get the attachment URL
        upload_url = f"{self.base_url}/{table}/{record_id}/{column_name}"
        files = {"file": (filename, BytesIO(file_data), mime_type)}

        resp = self.session.post(upload_url, headers=self.headers, files=files)
        logger.debug("Upload file response: %s %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        result = resp.json()
        logger.debug("Upload file result: %s", result)
        return result

    def link_records(
        self,
        table: str,
        record_id: int,
        link_field: str,
        linked_record_ids: list[int],
    ) -> dict[str, Any]:
        """
        Link records in a many-to-many relationship via NocoDB API.

        Args:
            table: The source table name (e.g., "Court_Decisions")
            record_id: The ID of the record in the source table
            link_field: The name of the link field (e.g., "Jurisdictions")
            linked_record_ids: List of IDs to link from the target table

        Returns:
            API response
        """
        logger.debug(
            "Linking records in table %s, record %s, field %s, linked IDs: %s",
            table,
            record_id,
            link_field,
            linked_record_ids,
        )

        # NocoDB API for linking: POST /api/v1/db/data/noco/{projectId}/{tableName}/{rowId}/{linkFieldName}
        # However, the simpler approach is to PATCH the record with the link field
        url = f"{self.base_url}/{table}/{record_id}"

        # For linking, we send the IDs as an array in the link field
        data = {link_field: linked_record_ids}

        resp = self.session.patch(url, headers=self.headers, json=data)
        logger.debug("Link records response: %s %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        result = resp.json()
        logger.debug("Link records result: %s", result)
        return result

    def list_jurisdictions(
        self,
        jurisdiction_value: str,
    ) -> list[int]:
        """
        Resolve jurisdiction IDs from various input formats (ID, ISO3 code, or Name).

        Args:
            jurisdiction_value: Can be an ID, ISO3 code (Alpha_3_Code), or Name

        Returns:
            List of jurisdiction IDs
        """
        if not jurisdiction_value or not jurisdiction_value.strip():
            return []

        # Try as numeric ID first
        try:
            jur_id = int(jurisdiction_value.strip())
            # Verify it exists
            rows = self.list_rows("Jurisdictions", limit=1)
            # TODO: Add filtering by ID once we implement proper filtering
            return [jur_id]
        except ValueError:
            pass

        # Search by Alpha_3_Code or Name
        # Note: This is a simplified implementation
        # In production, you'd want to use proper NocoDB filtering
        rows = self.list_rows("Jurisdictions", limit=1000)

        search_value = jurisdiction_value.strip().lower()
        for row in rows:
            alpha3 = row.get("Alpha_3_Code", "")
            name = row.get("Name", "")

            if (alpha3 and alpha3.lower() == search_value) or (name and name.lower() == search_value):
                row_id = row.get("id") or row.get("Id")
                if row_id:
                    return [int(row_id)]

        logger.warning("Could not find jurisdiction for value: %s", jurisdiction_value)
        return []
