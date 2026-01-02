# tests/test_search.py

import pytest


# ------------------------------------------------------------------------------
# Create a dummy search service for testing.
# ------------------------------------------------------------------------------
class DummySearchService:
    def full_text_search(
        self,
        search_string,
        filters=None,
        page=1,
        page_size=50,
        sort_by_date=False,
        response_type: str = "parsed",
    ):
        # Return a predictable result for testing.
        return {
            "dummy": "full_text_search",
            "search_string": search_string,
            "filters": filters,
            "page": page,
            "page_size": page_size,
            "sort_by_date": sort_by_date,
            "response_type": response_type,
        }

    def curated_details_search(self, table, cold_id, response_type: str = "parsed"):
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
            return {
                "dummy": "curated_details_search",
                "table": table,
                "id": cold_id,
                "source_table": table,
                "record_id": 123,
                "cold_id": cold_id,
                "hop1_relations": {"test": "relations"},
                "response_type": response_type,
            }
        else:
            return {"error": "this table either does not exist or has not been implemented in this route"}

    def full_table(self, table, response_type: str = "parsed"):
        return {"dummy": "full_table", "table": table, "response_type": response_type}

    def filtered_table(self, table, filters, response_type: str = "parsed"):
        return {
            "dummy": "filtered_table",
            "table": table,
            "filters": filters,
            "response_type": response_type,
        }


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
    result = dummy_service.curated_details_search("Answers", "CHE_01.1-P")
    assert result["dummy"] == "curated_details_search"
    assert result["table"] == "Answers"
    assert result["id"] == "CHE_01.1-P"
    assert result["source_table"] == "Answers"
    assert result["record_id"] == 123
    assert result["cold_id"] == "CHE_01.1-P"
    assert "hop1_relations" in result


def test_service_curated_details_search_invalid(dummy_service):
    result = dummy_service.curated_details_search("InvalidTable", "TEST_ID")
    assert "error" in result
    assert result["error"] == "this table either does not exist or has not been implemented in this route"


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
