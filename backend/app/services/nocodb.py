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
        field_id: str,
        file_data: bytes,
        filename: str,
        mime_type: str = "application/pdf",
        field_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Upload a file to a NocoDB attachment field using a two-step process:
        1. Upload file to NocoDB storage (v2 API) to get attachment metadata
        2. Update the record (v1 API) with the attachment metadata

        Args:
            table: Table ID
            record_id: Record ID
            field_id: Field ID (for fetching current attachments)
            file_data: Binary file data
            filename: Name of the file
            mime_type: MIME type
            field_name: Field name to use in PATCH (defaults to field_id if not provided)

        Reference: https://nocodb.com/docs/product-docs/developer-resources/rest-apis/upload-via-api
        """
        from io import BytesIO

        logger.debug(
            "Uploading file to table %s, record %s, field %s, filename %s",
            table,
            record_id,
            field_id,
            filename,
        )

        # Step 1: Upload file to NocoDB storage
        base_parts = self.base_url.split("/api/")
        if len(base_parts) >= 2:
            storage_base = base_parts[0]
            upload_url = f"{storage_base}/api/v2/storage/upload"
        else:
            upload_url = f"{self.base_url}/api/v2/storage/upload"

        files = {"file": (filename, BytesIO(file_data), mime_type)}

        logger.debug("Uploading file to NocoDB storage: %s", upload_url)
        resp = self.session.post(upload_url, headers=self.headers, files=files)
        logger.debug("Upload file response: %s %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
        upload_result = resp.json()
        logger.debug("Upload file result: %s", upload_result)

        # Step 2: Update the record with the attachment metadata
        update_url = f"{self.base_url}/{table}/{record_id}"

        # Get current attachments if any
        try:
            current_row = self.get_row(table, str(record_id))
            current_attachments = current_row.get(field_id, [])
            if not isinstance(current_attachments, list):
                current_attachments = []
        except Exception as e:
            logger.warning("Failed to get current attachments: %s. Starting with empty list.", e)
            current_attachments = []

        # Append new attachment(s)
        if isinstance(upload_result, list):
            new_attachments = current_attachments + upload_result
        else:
            new_attachments = current_attachments + [upload_result]

        # Use field_name for update if provided, otherwise use field_id
        update_field = field_name if field_name else field_id
        update_data = {update_field: new_attachments}

        logger.debug("Updating record with attachment using field '%s': %s", update_field, update_data)
        resp = self.session.patch(update_url, headers=self.headers, json=update_data)
        logger.debug("Update record response: %s %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
        result = resp.json()
        logger.debug("Update record result: %s", result)

        return result

    def link_records(
        self,
        table: str,
        record_id: int,
        field_id: str,
        linked_record_ids: list[int],
    ) -> dict[str, Any]:
        """
        Link records in a many-to-many relationship via NocoDB v2 API.

        Uses POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}

        Args:
            table: The source table ID (e.g., "mdmls7kc3a3w1vu")
            record_id: The ID of the record in the source table
            field_id: The link field ID (e.g., "c6rj8tua651icm0" for Jurisdictions)
            linked_record_ids: List of IDs to link from the target table

        Returns:
            API response
        """
        logger.debug(
            "Linking records in table %s, record %s, field %s, linked IDs: %s",
            table,
            record_id,
            field_id,
            linked_record_ids,
        )

        # Extract base URL for v2 API
        base_parts = self.base_url.split("/api/")
        if len(base_parts) >= 2:
            storage_base = base_parts[0]
            # Use v2 API endpoint structure
            url = f"{storage_base}/api/v2/tables/{table}/links/{field_id}/records/{record_id}"
        else:
            url = f"{self.base_url}/api/v2/tables/{table}/links/{field_id}/records/{record_id}"

        # Payload is an array of record IDs with capital "Id" per v2 API
        data = [{"Id": link_id} for link_id in linked_record_ids]

        logger.debug("Linking records via v2 API: %s with data: %s", url, data)
        resp = self.session.post(url, headers=self.headers, json=data)
        logger.debug("Link records response: %s %s", resp.status_code, resp.text[:400])
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
            # Verify it exists by fetching jurisdictions
            rows = self.list_rows("Jurisdictions", limit=1000)
            for row in rows:
                row_id = row.get("id") or row.get("Id")
                if row_id and int(row_id) == jur_id:
                    return [jur_id]
            # ID not found
            logger.warning("Jurisdiction ID %d not found", jur_id)
            return []
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
