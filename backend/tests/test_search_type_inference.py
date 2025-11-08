"""
Tests for search type inference functionality.
"""

import pytest


class TestSearchTypeInference:
    """Test type inference from search queries."""

    def test_infer_legislation_type(self):
        """Test that legislation keywords are correctly identified."""
        # Import only what we need to test
        from app.services.search import SearchService

        # Test the static method without initializing the service
        result = SearchService._infer_type_from_query(None, "Swiss legislation on contracts")
        assert result is not None
        assert "Domestic Instruments" in result

    def test_infer_court_decision_type(self):
        """Test that court decision keywords are correctly identified."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(None, "landmark court case on jurisdiction")
        assert result is not None
        assert "Court Decisions" in result

    def test_infer_literature_type(self):
        """Test that literature keywords are correctly identified."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(None, "academic article on choice of law")
        assert result is not None
        assert "Literature" in result

    def test_infer_international_instrument_type(self):
        """Test that international instrument keywords are correctly identified."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(
            None, "international treaty on arbitration"
        )
        assert result is not None
        assert "International Instruments" in result

    def test_no_type_inference_simple_query(self):
        """Test that simple queries without type keywords return None."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(None, "Switzerland")
        assert result is None

    def test_no_type_inference_empty_query(self):
        """Test that empty queries return None."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(None, "")
        assert result is None

    def test_multiple_types_inferred(self):
        """Test that multiple types can be inferred from a single query."""
        from app.services.search import SearchService

        result = SearchService._infer_type_from_query(
            None, "court case about legislation"
        )
        assert result is not None
        assert "Court Decisions" in result
        assert "Domestic Instruments" in result

    def test_prioritize_results_by_type(self):
        """Test that results are correctly prioritized by type."""
        from app.services.search import SearchService

        # Create mock results with different source tables
        mock_results = [
            {"source_table": "Court Decisions", "id": 1, "rank": 0.9},
            {"source_table": "Answers", "id": 2, "rank": 0.8},
            {"source_table": "Literature", "id": 3, "rank": 0.7},
            {"source_table": "Domestic Instruments", "id": 4, "rank": 0.6},
        ]

        # Prioritize Answers
        prioritized = SearchService._prioritize_results_by_type(
            None, mock_results, ["Answers"]
        )
        assert prioritized[0]["source_table"] == "Answers"
        assert len(prioritized) == 4

        # Prioritize multiple types
        prioritized = SearchService._prioritize_results_by_type(
            None, mock_results, ["Literature", "Domestic Instruments"]
        )
        assert prioritized[0]["source_table"] == "Literature"
        assert prioritized[1]["source_table"] == "Domestic Instruments"
        assert prioritized[2]["source_table"] == "Court Decisions"
        assert prioritized[3]["source_table"] == "Answers"

    def test_prioritize_maintains_relative_order(self):
        """Test that relative order within priority groups is maintained."""
        from app.services.search import SearchService

        mock_results = [
            {"source_table": "Answers", "id": 1, "rank": 0.9},
            {"source_table": "Answers", "id": 2, "rank": 0.8},
            {"source_table": "Literature", "id": 3, "rank": 0.7},
        ]

        prioritized = SearchService._prioritize_results_by_type(
            None, mock_results, ["Answers"]
        )
        # Both Answers should appear first, in original order
        assert prioritized[0]["id"] == 1
        assert prioritized[1]["id"] == 2
        assert prioritized[2]["source_table"] == "Literature"
