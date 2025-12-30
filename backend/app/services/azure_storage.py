"""
Azure Blob Storage helper for downloading files using managed identity.
"""

import logging
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


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
