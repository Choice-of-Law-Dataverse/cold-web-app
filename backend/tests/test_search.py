# tests/test_search.py

import sys
from pathlib import Path

# Ensure the project root is in sys.path so we can import the app package.
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import the FastAPI app, JWT dependency, and the search routes
from app.main import app
from app.auth import verify_jwt_token
from app.routes import search as search_routes
from app.services.search import SearchService


# ------------------------------------------------------------------------------
# Override the JWT dependency for testing.
# ------------------------------------------------------------------------------
def override_verify_jwt_token():
    # Simply return a dummy user payload (or do nothing)
    return {"sub": "test_user"}


app.dependency_overrides[verify_jwt_token] = override_verify_jwt_token


# ------------------------------------------------------------------------------
# Create a dummy search service to override the one used in routes.
# ------------------------------------------------------------------------------
class DummySearchService:
    def full_text_search(self, search_string, filters=None, page=1, page_size=50, sort_by_date=False):
        # Return a predictable result for testing.
        return {
            "dummy": "full_text_search",
            "search_string": search_string,
            "filters": filters,
            "page": page,
            "page_size": page_size,
            "sort_by_date": sort_by_date,
        }

    def curated_details_search(self, table, id):
        # For allowed table names, return dummy data; otherwise, return an error dict.
        allowed_tables = [
            "Answers",
            "Legislation",
            "Legal provisions",
            "Court decisions",
            "Jurisdictions",
            "Literature",
        ]
        if table in allowed_tables:
            return {"dummy": "curated_details_search", "table": table, "id": id}
        else:
            return {
                "error": "this table either does not exist or has not been implemented in this route"
            }

    def full_table(self, table):
        return {"dummy": "full_table", "table": table}

    def filtered_table(self, table, filters):
        return {"dummy": "filtered_table", "table": table, "filters": filters}


# Override the search_service instance in the search routes with our dummy service.
search_routes.search_service = DummySearchService()

# Initialize the TestClient with our FastAPI app.
client = TestClient(app)

# ------------------------------------------------------------------------------
# Tests for the search endpoints
# ------------------------------------------------------------------------------


def test_full_text_search():
    """
    Test the POST /search/ endpoint for full text search.
    """
    payload = {
        "search_string": "example search",
        "filters": [
            {
                # Assuming your filter items have a "column" and "values" field.
                "column": "themes",
                "values": ["theme1", "theme2"],
            }
        ],
    }
    response = client.post("/search/", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["dummy"] == "full_text_search"
    assert json_data["search_string"] == "example search"
    assert json_data["filters"] == payload["filters"]


def test_curated_details_search_valid():
    """
    Test the POST /search/details endpoint with a valid table.
    """
    payload = {"table": "Answers", "id": "1"}  # id is now a string
    response = client.post("/search/details", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["dummy"] == "curated_details_search"
    assert json_data["table"] == "Answers"
    assert json_data["id"] == "1"


def test_curated_details_search_invalid():
    """
    Test the POST /search/details endpoint with an invalid table.
    """
    payload = {"table": "NonExistent", "id": "1"}  # id as a string
    response = client.post("/search/details", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "error" in json_data
    assert (
        json_data["error"]
        == "this table either does not exist or has not been implemented in this route"
    )


def test_full_table_without_filters():
    """
    Test the POST /search/full_table endpoint without providing filters.
    """
    payload = {"table": "Answers", "filters": None}
    response = client.post("/search/full_table", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    # Since filters is None, the endpoint should call full_table().
    assert json_data["dummy"] == "full_table"
    assert json_data["table"] == "Answers"


def test_full_table_with_filters():
    """
    Test the POST /search/full_table endpoint when filters are provided.
    """
    payload = {
        "table": "Answers",
        "filters": [
            {"column": "name", "value": "John Doe"}  # changed "value" to "values"
        ],
    }
    response = client.post("/search/full_table", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["dummy"] == "filtered_table"
    assert json_data["table"] == "Answers"
    assert json_data["filters"] == payload["filters"]


def test_full_table_missing_table():
    """
    Test the POST /search/full_table endpoint when no table is provided.
    Expect a 400 error.
    """
    payload = {"table": "", "filters": None}
    response = client.post("/search/full_table", json=payload)
    # The route raises an HTTPException with status_code 400.
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["detail"] == "No table provided"


# ------------------------------------------------------------------------------
# Tests for the SearchService functions (using the dummy service)
# ------------------------------------------------------------------------------


@pytest.fixture
def dummy_service():
    return DummySearchService()


def test_service_full_text_search(dummy_service):
    result = dummy_service.full_text_search("test", [])
    assert result["dummy"] == "full_text_search"
    assert result["search_string"] == "test"
    assert result["filters"] == []


def test_service_curated_details_search_valid(dummy_service):
    result = dummy_service.curated_details_search("Answers", 123)
    assert result["dummy"] == "curated_details_search"
    assert result["table"] == "Answers"
    assert result["id"] == 123


def test_service_curated_details_search_invalid(dummy_service):
    result = dummy_service.curated_details_search("InvalidTable", 123)
    assert "error" in result
    assert (
        result["error"]
        == "this table either does not exist or has not been implemented in this route"
    )


def test_service_full_table(dummy_service):
    result = dummy_service.full_table("Answers")
    assert result["dummy"] == "full_table"
    assert result["table"] == "Answers"


def test_service_filtered_table(dummy_service):
    filters = [{"column": "name", "value": "Alice"}]
    result = dummy_service.filtered_table("Answers", filters)
    assert result["dummy"] == "filtered_table"
    assert result["table"] == "Answers"
    assert result["filters"] == filters
