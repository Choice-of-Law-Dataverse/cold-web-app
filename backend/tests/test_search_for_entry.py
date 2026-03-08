#!/usr/bin/env python3

import logging
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.search import SearchService

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skip(reason="Integration tests requiring real database - run manually with test DB")


def test_get_entity_detail_integration():
    search_service = SearchService()

    test_cases = [
        {"table": "Answers", "cold_id": "CHE_01.1-P"},
        {"table": "Court Decisions", "cold_id": "CD-CHE-1020"},
        {"table": "Questions", "cold_id": "Q-01.1"},
    ]

    for test_case in test_cases:
        table = test_case["table"]
        cold_id = test_case["cold_id"]

        result = search_service.get_entity_detail(table, cold_id)

        if result is None:
            logger.debug(f"No record found for {table} / {cold_id} (might be expected)")
        else:
            logger.debug(f"Found {result.get('source_table')} id={result.get('id')}")
            relations = result.get("relations", {})
            non_empty = {k: len(v) for k, v in relations.items() if v}
            logger.debug(f"Relations: {non_empty}")


def test_entity_detail_structure():
    search_service = SearchService()

    result = search_service.get_entity_detail("Answers", "CHE_01.1-P")

    if result is not None:
        assert "source_table" in result
        assert "id" in result
        assert "cold_id" in result
        assert "relations" in result

        relations = result["relations"]
        assert isinstance(relations, dict)
        assert "answers" in relations
        assert "jurisdictions" in relations
        assert "themes" in relations
