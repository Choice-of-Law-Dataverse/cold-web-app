import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

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
    
    with patch('app.services.sitemap.SitemapService._get_table_ids') as mock_get_ids:
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
        
        # Make a GET request to the sitemap URLs endpoint
        response = client.get("/api/v1/sitemap/urls")
        
        # Assert that the request was successful
        assert response.status_code == 200
        
        # Get the response data
        data = response.json()
        
        # Assert that the response has the expected structure
        assert "alpha" in data
        assert "beta" in data
        assert "tables_processed" in data
        
        # Assert alpha subdictionary structure
        alpha_data = data["alpha"]
        assert "urls" in alpha_data
        assert "total_count" in alpha_data
        assert "base_url" in alpha_data
        assert alpha_data["base_url"] == "https://alpha.cold.global"
        
        # Assert beta subdictionary structure
        beta_data = data["beta"]
        assert "urls" in beta_data
        assert "total_count" in beta_data
        assert "base_url" in beta_data
        assert beta_data["base_url"] == "https://www.cold.global"
        
        # Assert that URLs are generated correctly for alpha
        alpha_urls = alpha_data["urls"]
        assert "https://alpha.cold.global/question/MSR_16.3-TC" in alpha_urls
        assert "https://alpha.cold.global/literature/132" in alpha_urls
        assert "https://alpha.cold.global/regional-instrument/RI-OHA-3" in alpha_urls
        assert "https://alpha.cold.global/international-instrument/II-HCC-1" in alpha_urls
        assert "https://alpha.cold.global/court-decision/CD-ISR-525" in alpha_urls
        assert "https://alpha.cold.global/domestic-instrument/DI-FRA-63" in alpha_urls
        
        # Assert that URLs are generated correctly for beta
        beta_urls = beta_data["urls"]
        assert "https://www.cold.global/question/MSR_16.3-TC" in beta_urls
        assert "https://www.cold.global/literature/132" in beta_urls
        assert "https://www.cold.global/regional-instrument/RI-OHA-3" in beta_urls
        assert "https://www.cold.global/international-instrument/II-HCC-1" in beta_urls
        assert "https://www.cold.global/court-decision/CD-ISR-525" in beta_urls
        assert "https://www.cold.global/domestic-instrument/DI-FRA-63" in beta_urls
        
        # Assert total count matches expected for both
        assert alpha_data["total_count"] == 12  # 2 URLs per table * 6 tables
        assert beta_data["total_count"] == 12  # 2 URLs per table * 6 tables
        
        # Assert all expected tables were processed
        expected_tables = [
            "Answers", "Literature", "Regional Instruments", 
            "International Instruments", "Court Decisions", "Domestic Instruments"
        ]
        assert set(data["tables_processed"]) == set(expected_tables)


def test_sitemap_urls_endpoint_empty_database():
    """Test the sitemap URLs endpoint when database returns no results."""
    with patch('app.services.sitemap.SitemapService._get_table_ids') as mock_get_ids:
        # Configure the mock to return empty results
        mock_get_ids.return_value = []
        
        # Make a GET request to the sitemap URLs endpoint
        response = client.get("/api/v1/sitemap/urls")
        
        # Assert that the request was successful
        assert response.status_code == 200
        
        # Get the response data
        data = response.json()
        
        # Assert that the response has the expected structure with empty results
        assert "alpha" in data
        assert "beta" in data
        assert data["alpha"]["urls"] == []
        assert data["alpha"]["total_count"] == 0
        assert data["beta"]["urls"] == []
        assert data["beta"]["total_count"] == 0
        assert len(data["tables_processed"]) == 6  # All tables should still be processed
