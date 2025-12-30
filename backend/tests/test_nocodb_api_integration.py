#!/usr/bin/env python3
"""
Test NocoDB service integration for case analyzer.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.nocodb import NocoDBService


class TestNocoDBService:
    """Tests for NocoDB service methods."""

    def test_create_row_success(self):
        """Test successful row creation via NocoDB API."""
        # Mock the HTTP session
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "Case_Citation": "Test v. Case"}
        mock_response.text = '{"id": 123}'
        mock_session.post.return_value = mock_response

        with patch("app.services.nocodb.http_session_manager.get_session", return_value=mock_session):
            service = NocoDBService(base_url="https://test.nocodb.com", api_token="test-token")

            # Test data
            data = {
                "Case_Citation": "Test v. Case",
                "Abstract": "Test abstract",
            }

            result = service.create_row("Court_Decisions", data)

            # Verify the API was called correctly
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "https://test.nocodb.com/Court_Decisions"
            assert call_args[1]["json"] == data
            assert call_args[1]["headers"]["xc-token"] == "test-token"

            # Verify the response
            assert result["id"] == 123
            assert result["Case_Citation"] == "Test v. Case"

    def test_upload_file_success(self):
        """Test successful file upload to NocoDB."""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"url": "https://nocodb.com/files/test.pdf", "title": "test.pdf"}]
        mock_response.text = '[{"url": "https://nocodb.com/files/test.pdf"}]'
        mock_session.post.return_value = mock_response

        with patch("app.services.nocodb.http_session_manager.get_session", return_value=mock_session):
            service = NocoDBService(base_url="https://test.nocodb.com", api_token="test-token")

            # Test file upload
            file_data = b"PDF content here"
            result = service.upload_file(
                table="Court_Decisions",
                record_id=123,
                column_name="Official_Source_PDF",
                file_data=file_data,
                filename="test.pdf",
                mime_type="application/pdf",
            )

            # Verify the API was called correctly
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "https://test.nocodb.com/Court_Decisions/123/Official_Source_PDF"
            assert "files" in call_args[1]

            # Verify the response
            assert result[0]["url"] == "https://nocodb.com/files/test.pdf"

    def test_link_records_success(self):
        """Test linking records via NocoDB API."""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "Jurisdictions": [1, 2]}
        mock_response.text = '{"id": 123}'
        mock_session.patch.return_value = mock_response

        with patch("app.services.nocodb.http_session_manager.get_session", return_value=mock_session):
            service = NocoDBService(base_url="https://test.nocodb.com", api_token="test-token")

            # Test linking
            result = service.link_records(
                table="Court_Decisions",
                record_id=123,
                link_field="Jurisdictions",
                linked_record_ids=[1, 2],
            )

            # Verify the API was called correctly
            mock_session.patch.assert_called_once()
            call_args = mock_session.patch.call_args
            assert call_args[0][0] == "https://test.nocodb.com/Court_Decisions/123"
            assert call_args[1]["json"] == {"Jurisdictions": [1, 2]}

            # Verify the response
            assert result["id"] == 123
            assert result["Jurisdictions"] == [1, 2]

    def test_list_jurisdictions_by_name(self):
        """Test resolving jurisdiction by name."""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {"id": 1, "Name": "United States", "Alpha_3_Code": "USA"},
                {"id": 2, "Name": "United Kingdom", "Alpha_3_Code": "GBR"},
            ]
        }
        mock_session.get.return_value = mock_response

        with patch("app.services.nocodb.http_session_manager.get_session", return_value=mock_session):
            service = NocoDBService(base_url="https://test.nocodb.com", api_token="test-token")

            # Test by name
            result = service.list_jurisdictions("United Kingdom")
            assert result == [2]

            # Test by ISO3 code
            result = service.list_jurisdictions("USA")
            assert result == [1]

            # Test not found
            result = service.list_jurisdictions("NonExistent")
            assert result == []


class TestAzureStorageIntegration:
    """Tests for Azure Blob Storage integration."""

    def test_download_blob_url_parsing(self):
        """Test URL parsing for Azure blob storage."""
        from app.services.azure_storage import download_blob_with_managed_identity

        # Test with invalid URL
        with pytest.raises(ValueError, match="Invalid blob URL"):
            download_blob_with_managed_identity("not-a-url")

        # Test with non-blob URL
        with pytest.raises(ValueError, match="Invalid Azure blob storage URL"):
            download_blob_with_managed_identity("https://example.com/file.pdf")

        # Test with incomplete path
        with pytest.raises(ValueError, match="Invalid blob path"):
            download_blob_with_managed_identity("https://account.blob.core.windows.net/container")

    @patch("app.services.azure_storage.BlobServiceClient")
    @patch("app.services.azure_storage.DefaultAzureCredential")
    def test_download_blob_success(self, mock_credential, mock_blob_service):
        """Test successful blob download."""
        from app.services.azure_storage import download_blob_with_managed_identity

        # Mock the blob client
        mock_blob_data = b"PDF content from Azure"
        mock_download = Mock()
        mock_download.readall.return_value = mock_blob_data

        mock_blob_client = Mock()
        mock_blob_client.download_blob.return_value = mock_download

        mock_service_instance = Mock()
        mock_service_instance.get_blob_client.return_value = mock_blob_client
        mock_blob_service.return_value = mock_service_instance

        # Test download
        url = "https://choiceoflaw.blob.core.windows.net/cold-case-analysis/test-file.pdf"
        result = download_blob_with_managed_identity(url)

        # Verify
        assert result == mock_blob_data
        mock_blob_service.assert_called_once()
        mock_service_instance.get_blob_client.assert_called_once_with(
            container="cold-case-analysis", blob="test-file.pdf"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
