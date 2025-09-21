#!/usr/bin/env python3
"""
Comprehensive test script for all table transformations.
"""

import logging
import os
import sys

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.mapping_repository import get_mapping_repository
from app.services.transformers import DataTransformerFactory

logger = logging.getLogger(__name__)


def test_all_supported_tables():
    """Test all supported table transformations."""
    logger.debug("=== TESTING ALL SUPPORTED TABLES ===")

    # Get mapping repository
    repo = get_mapping_repository()
    supported_tables = repo.get_supported_tables()

    logger.debug(f"Supported tables: {supported_tables}")

    # Test data for each table type
    test_data = {
        "Answers": {
            "source_table": "Answers",
            "CoLD_ID": "ABW_34-FV",
            "Answer": "No data",
            "related_jurisdictions": [{"Name": "Aruba", "Alpha_3_Code": "ABW", "ncRecordId": "rec123"}],
            "related_questions": [
                {
                    "Question": "Test question",
                    "Primary_Theme": "FV",
                    "Question_Number": "34",
                }
            ],
            "related_themes": [
                {"Theme": "Consumer contracts"},
                {"Theme": "Employment contracts"},
            ],
        },
        "Court Decisions": {
            "source_table": "Court Decisions",
            "CoLD_ID": "CD-GBR-1167",
            "Case_Citation": "Test v Test [2007] EWCA Civ 291",
            "Case_Title": "Test v Test",
            "related_jurisdictions": [
                {
                    "Name": "United Kingdom",
                    "Alpha_3_Code": "GBR",
                    "ncRecordId": "rec456",
                }
            ],
            "related_themes": [{"Theme": "Party autonomy"}, {"Theme": "Rules of law"}],
        },
        "Domestic Instruments": {
            "source_table": "Domestic Instruments",
            "CoLD_ID": "DI-TCD-29",
            "Title__in_English_": "Test Law",
            "Status": "In force",
            "related_jurisdictions": [
                {
                    "Name": "Chad",
                    "Alpha_3_Code": "TCD",
                    "Type": "State",
                    "ncRecordId": "rec789",
                }
            ],
            "Compatible_With_the_HCCH_Principles_": False,
        },
    }

    for table_name in supported_tables:
        if table_name in test_data:
            logger.debug(f"\n--- Testing {table_name} ---")

            mock_data = test_data[table_name]
            transformed = DataTransformerFactory.transform_result(table_name, mock_data)

            logger.debug(f"Original fields: {len(mock_data)}")
            logger.debug(f"Transformed fields: {len(transformed)}")
            logger.debug(f"ID field: {transformed.get('id', 'NOT FOUND')}")
            logger.debug(f"Source table: {transformed.get('source_table', 'NOT FOUND')}")

            # Check if transformation actually happened
            if len(transformed) > len(mock_data):
                logger.debug("✓ Transformation added fields")
            else:
                logger.debug("? Transformation may not have expanded fields")


def test_factory_fallback():
    """Test factory fallback mechanism."""
    logger.debug("\n=== TESTING FACTORY FALLBACK MECHANISM ===")

    # Test with a table that has explicit transformer
    answers_data = {"source_table": "Answers", "CoLD_ID": "TEST-001", "Answer": "Yes"}
    transformed_answers = DataTransformerFactory.transform_result("Answers", answers_data)
    logger.debug(f"Answers transformation (explicit): {len(transformed_answers)} fields")

    # Test with a table that only has configuration
    if get_mapping_repository().has_mapping("Questions"):
        questions_data = {
            "source_table": "Questions",
            "CoLD_ID": "Q-001",
            "Question": "Test question?",
        }
        transformed_questions = DataTransformerFactory.transform_result("Questions", questions_data)
        logger.debug(f"Questions transformation (config-only): {len(transformed_questions)} fields")

    # Test with completely unknown table
    unknown_data = {"source_table": "Unknown", "id": 123, "data": "test"}
    transformed_unknown = DataTransformerFactory.transform_result("Unknown", unknown_data)
    logger.debug(f"Unknown table (no transformation): {transformed_unknown == unknown_data}")


def test_mapping_configurations():
    """Test mapping configuration loading and structure."""
    logger.debug("\n=== TESTING MAPPING CONFIGURATIONS ===")

    repo = get_mapping_repository()

    for table_name in repo.get_supported_tables():
        mapping = repo.get_mapping(table_name)
        if mapping is None:
            logger.debug(f"\n--- {table_name} Configuration ---")
            logger.debug("No mapping loaded; skipping.")
            continue

        logger.debug(f"\n--- {table_name} Configuration ---")
        logger.debug(f"Version: {mapping.get('version')}")
        logger.debug(f"Description: {mapping.get('description', 'No description')[:60]}...")

        mappings = mapping.get("mappings", {})
        logger.debug(f"Direct mappings: {len(mappings.get('direct_mappings', {}))}")
        logger.debug(f"Conditional mappings: {len(mappings.get('conditional_mappings', {}))}")
        logger.debug(f"Nested mappings: {len(mappings.get('nested_mappings', {}))}")
        logger.debug(f"Complex mappings: {len(mappings.get('complex_mappings', {}))}")
        logger.debug(f"User mappings: {len(mappings.get('user_mappings', {}))}")
        logger.debug(f"Boolean mappings: {len(mappings.get('boolean_mappings', {}))}")

        post_processing = mapping.get("post_processing", {})
        logger.debug(f"Post-processing rules: {len(post_processing)}")


def run_performance_test():
    """Run a simple performance test."""
    logger.debug("\n=== PERFORMANCE TEST ===")
    import time

    # Create test data for all tables
    test_datasets = {
        "Answers": {
            "source_table": "Answers",
            "CoLD_ID": "TEST-001",
            "Answer": "Test answer",
            "related_jurisdictions": [{"Name": "Test Country", "Alpha_3_Code": "TST"}],
            "related_questions": [{"Question": "Test?", "Primary_Theme": "T"}],
            "related_themes": [{"Theme": "Test theme"}],
        },
        "Court Decisions": {
            "source_table": "Court Decisions",
            "CoLD_ID": "CD-TST-001",
            "Case_Citation": "Test v Test",
            "related_jurisdictions": [{"Name": "Test Country", "Alpha_3_Code": "TST"}],
        },
        "Domestic Instruments": {
            "source_table": "Domestic Instruments",
            "CoLD_ID": "DI-TST-001",
            "Title__in_English_": "Test Law",
            "related_jurisdictions": [{"Name": "Test Country", "Alpha_3_Code": "TST", "Type": "State"}],
        },
    }

    num_iterations = 100
    total_time = 0

    for table_name, test_data in test_datasets.items():
        start_time = time.time()

        for _ in range(num_iterations):
            DataTransformerFactory.transform_result(table_name, test_data)

        end_time = time.time()
        table_time = end_time - start_time
        total_time += table_time

        logger.debug(
            f"{table_name}: {table_time:.4f}s for {num_iterations} transformations ({(table_time / num_iterations) * 1000:.2f}ms avg)"  # noqa: E501
        )

    logger.debug(f"Total time: {total_time:.4f}s")
    logger.debug(f"Average per transformation: {(total_time / (num_iterations * len(test_datasets))) * 1000:.2f}ms")


if __name__ == "__main__":
    try:
        test_all_supported_tables()
        test_factory_fallback()
        test_mapping_configurations()
        run_performance_test()
        logger.debug("\n=== ALL COMPREHENSIVE TESTS COMPLETED ===")
    except Exception as e:
        logger.debug(f"Test error: {e}")
        import traceback

        traceback.print_exc()
