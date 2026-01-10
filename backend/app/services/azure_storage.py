"""
Azure Blob Storage helper for downloading and uploading files using managed identity.
"""

import logging
import uuid
from datetime import UTC, datetime
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger(__name__)

# Storage configuration - these should be set via environment variables in production
DEFAULT_STORAGE_ACCOUNT = "coldstorageaccount"
DEFAULT_CONTAINER = "case-analyzer-uploads"


def download_blob_with_managed_identity(blob_url: str) -> bytes:
    """
    Download a blob from Azure Storage using managed identity (DefaultAzureCredential).

    Args:
        blob_url: Full URL to the blob (e.g., https://account.blob.core.windows.net/container/blob.pdf)

    Returns:
        bytes: The blob content

    Raises:
        ValueError: If the URL is invalid
        Exception: If download fails
    """
    logger.info("Downloading blob from URL: %s", blob_url)

    # Parse the URL to extract account, container, and blob name
    parsed = urlparse(blob_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid blob URL: {blob_url}")

    # Ensure HTTPS is used for secure connections
    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS URLs are supported for Azure blob storage: {blob_url}")

    # Extract storage account name from hostname (e.g., account.blob.core.windows.net)
    hostname_parts = parsed.netloc.split(".")
    if len(hostname_parts) < 3 or hostname_parts[1] != "blob":
        raise ValueError(f"Invalid Azure blob storage URL: {blob_url}")

    account_name = hostname_parts[0]
    account_url = f"https://{account_name}.blob.core.windows.net"

    # Extract container and blob name from path
    # Path format: /container/blob/path/to/file.pdf
    path_parts = parsed.path.lstrip("/").split("/", 1)
    if len(path_parts) < 2:
        raise ValueError(f"Invalid blob path in URL: {blob_url}")

    container_name = path_parts[0]
    blob_name = path_parts[1]

    logger.debug(
        "Parsed blob URL: account=%s, container=%s, blob=%s",
        account_name,
        container_name,
        blob_name,
    )

    try:
        # Use DefaultAzureCredential which will try managed identity first
        credential = DefaultAzureCredential()

        # Create BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

        # Get blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Download blob content
        logger.info("Downloading blob: %s/%s", container_name, blob_name)
        blob_data = blob_client.download_blob().readall()

        logger.info("Successfully downloaded %d bytes from blob", len(blob_data))
        return blob_data

    except Exception as e:
        logger.error("Failed to download blob from %s: %s", blob_url, str(e))
        raise


def upload_blob_with_managed_identity(
    pdf_bytes: bytes,
    filename: str,
    storage_account: str | None = None,
    container: str | None = None,
) -> str:
    """
    Upload a PDF to Azure Storage using managed identity.

    Args:
        pdf_bytes: PDF file content as bytes
        filename: Original filename (used to generate unique blob name)
        storage_account: Azure storage account name (defaults to DEFAULT_STORAGE_ACCOUNT)
        container: Container name (defaults to DEFAULT_CONTAINER)

    Returns:
        str: Full Azure blob URL

    Raises:
        Exception: If upload fails
    """
    storage_account = storage_account or DEFAULT_STORAGE_ACCOUNT
    container = container or DEFAULT_CONTAINER
    account_url = f"https://{storage_account}.blob.core.windows.net"

    # Generate unique blob name with timestamp and UUID
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_extension = filename.rsplit(".", 1)[-1] if "." in filename else "pdf"
    blob_name = f"case-analysis/{timestamp}_{unique_id}.{file_extension}"

    logger.info("Uploading %d bytes to blob: %s/%s", len(pdf_bytes), container, blob_name)

    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)

        blob_client.upload_blob(pdf_bytes, overwrite=False, content_settings=ContentSettings(content_type="application/pdf"))

        blob_url = f"{account_url}/{container}/{blob_name}"
        logger.info("Successfully uploaded blob to: %s", blob_url)
        return blob_url

    except Exception as e:
        logger.error("Failed to upload blob: %s", str(e))
        raise
