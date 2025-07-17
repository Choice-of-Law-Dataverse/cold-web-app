import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import date

# Import your FastAPI app and the dependency to override
from app.main import app
from app.auth import verify_jwt_token


# Create an override function that simulates successful JWT verification.
def override_verify_jwt_token():
    return {"sub": "test_user"}


# Apply the dependency override.
app.dependency_overrides[verify_jwt_token] = override_verify_jwt_token

# Initialize the TestClient with the FastAPI app.
client = TestClient(app)


def test_sitemap_urls_endpoint():
    """Test the sitemap URLs endpoint returns the expected structure."""
    # Mock the database response
    mock_db_results = {
        "Answers": [{"ID": "MSR_16.3-TC"}, {"ID": "MSR_15.2-AA"}],
        "Literature": [{"ID": "132"}, {"ID": "245"}],
        "Regional Instruments": [{"ID": "RI-OHA-3"}, {"ID": "RI-EUR-1"}],
        "International Instruments": [{"ID": "II-HCC-1"}, {"ID": "II-UNC-2"}],
        "Court Decisions": [{"ID": "CD-ISR-525"}, {"ID": "CD-USA-123"}],
        "Domestic Instruments": [{"ID": "DI-FRA-63"}, {"ID": "DI-GER-45"}]
    }
    
    # Patch dynamic and static methods for predictable output
    with patch('app.services.sitemap.SitemapService._get_table_ids') as mock_get_ids, \
         patch('app.services.sitemap.SitemapService._get_static_paths', return_value=[]):
        # Configure the mock to return different IDs for each table
        def side_effect(table_name):
            if table_name == "Answers":
                return ["MSR_16.3-TC", "MSR_15.2-AA"]
            elif table_name == "Literature":
                return ["132", "245"]
            elif table_name == "Regional Instruments":
                return ["RI-OHA-3", "RI-EUR-1"]
            elif table_name == "International Instruments":
                return ["II-HCC-1", "II-UNC-2"]
            elif table_name == "Court Decisions":
                return ["CD-ISR-525", "CD-USA-123"]
            elif table_name == "Domestic Instruments":
                return ["DI-FRA-63", "DI-GER-45"]
            return []
        
        mock_get_ids.side_effect = side_effect
        # Request sitemap entries
        response = client.get("/api/v1/sitemap/urls")
        assert response.status_code == 200
        data = response.json()
        # Should be a list of entries
        assert isinstance(data, list)
        # Expect 2 IDs per 6 tables
        expected_count = 6 * 2
        assert len(data) == expected_count
        # Validate each dynamic entry has correct loc and lastmod
        mapping = {
            "Answers": "/question/",
            "Literature": "/literature/",
            "Regional Instruments": "/regional-instrument/",
            "International Instruments": "/international-instrument/",
            "Court Decisions": "/court-decision/",
            "Domestic Instruments": "/domestic-instrument/"
        }
        for table, prefix in mapping.items():
            for id_val in side_effect(table):
                entry = {"loc": f"{prefix}{id_val}", "lastmod": date.today().isoformat()}
                assert entry in data


def test_sitemap_urls_endpoint_empty_database():
    """Test the sitemap URLs endpoint when database returns no results."""
    with patch('app.services.sitemap.SitemapService._get_table_ids', return_value=[]), \
         patch('app.services.sitemap.SitemapService._get_static_paths', return_value=[]):
        response = client.get("/api/v1/sitemap/urls")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # No entries when no dynamic IDs and no static pages
        assert data == []
