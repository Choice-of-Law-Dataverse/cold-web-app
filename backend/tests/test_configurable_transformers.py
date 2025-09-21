#!/usr/bin/env python3
"""
Test script for the configuration-driven transformer system.
"""

import json
import os
import sys

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.configurable_transformer import ConfigurableTransformer
from app.services.mapping_repository import MappingRepository
from app.services.transformers import AnswersTransformer, DataTransformerFactory


def create_mock_answers_result():
    """Create a mock answers result for testing."""
    return {
        "source_table": "Answers",
        "id": 3098,
        "rank": 1,
        "result_date": "2025-06-16",
        "Answer": "No data",
        "CoLD_ID": "ABW_34-FV",
        "Created": "2023-12-04T14:54:00",
        "nc_order": 1682,
        "To_Review_": None,
        "created_at": "2025-06-10T15:09:06",
        "created_by": "usaf3dew23c77lgf",
        "ncRecordId": "recBATNtCRMiZ2fp7",
        "updated_at": "2025-06-16T13:32:55",
        "updated_by": "usaf3dew23c77lgf",
        "related_themes": [
            {
                "id": 4,
                "Theme": "Consumer contracts",
                "Created": "2025-03-21T08:57:00"
            },
            {
                "id": 15,
                "Theme": "Employment contracts",
                "Created": "2025-03-21T08:57:00"
            }
        ],
        "More_Information": None,
        "Question_CoLD_ID": "34-FV",
        "related_questions": [
            {
                "id": 30,
                "Created": "2023-11-27T13:03:00",
                "Question": "Is further guidance on applicable law in international contracts providing protection to weaker parties necessary?",
                "nc_order": 1,
                "Theme_Code": "Rev",
                "created_at": "2025-06-10T15:08:37",
                "ncRecordId": "rec0XQRyxFGp9he5X",
                "Primary_Theme": "FV",
                "Question_Number": "34",
                "Answering_Options": "Yes, No, No strong opinions"
            }
        ],
        "Interesting_Answer": 0,
        "related_jurisdictions": [
            {
                "id": 52,
                "Done": None,
                "Name": "Aruba",
                "Type": "State",
                "Region": "South & Latin America",
                "Created": "2021-03-07T14:24:00",
                "nc_order": 52,
                "ncRecordId": "recFTvThFw38M7URq",
                "Irrelevant_": True,
                "Alpha_3_Code": "ABW",
                "Legal_Family": None,
                "North_South_Divide": "Global South"
            }
        ],
        "Jurisdictions_Alpha_3_Code": "ABW"
    }

def test_mapping_repository():
    """Test the mapping repository functionality."""
    print("=== TESTING MAPPING REPOSITORY ===")

    # Test loading mappings
    repo = MappingRepository()

    print(f"Supported tables: {repo.get_supported_tables()}")
    print(f"Has Answers mapping: {repo.has_mapping('Answers')}")
    print(f"Has Unknown mapping: {repo.has_mapping('Unknown')}")

    # Get Answers mapping
    answers_mapping = repo.get_mapping("Answers")
    if answers_mapping:
        print(f"Answers mapping version: {answers_mapping.get('version')}")
        print(f"Answers mapping description: {answers_mapping.get('description')}")
        print(f"Direct mappings count: {len(answers_mapping.get('mappings', {}).get('direct_mappings', {}))}")
    else:
        print("No Answers mapping found")

def test_configurable_transformer():
    """Test the configurable transformer."""
    print("\n=== TESTING CONFIGURABLE TRANSFORMER ===")

    transformer = ConfigurableTransformer()
    mock_result = create_mock_answers_result()

    # Transform using configuration
    transformed = transformer.transform("Answers", mock_result)

    print("Configuration-driven transformation result:")
    print(json.dumps(transformed, indent=2, default=str))

    # Verify key mappings
    expected_mappings = {
        "source_table": "Answers",
        "id": "ABW_34-FV",
        "ID": "ABW_34-FV",
        "Answer": "No data",
        "Jurisdictions": "Aruba",
        "Jurisdictions Alpha-3 code": "ABW",
        "Question": "Is further guidance on applicable law in international contracts providing protection to weaker parties necessary?",
        "Questions Theme Code": "FV",
        "Themes": "Consumer contracts, Employment contracts",
        "Jurisdictions Irrelevant": "Yes"
    }

    print("\n=== VERIFICATION ===")
    for key, expected_value in expected_mappings.items():
        actual_value = transformed.get(key)
        status = "✓" if actual_value == expected_value else "✗"
        print(f"{status} {key}: expected='{expected_value}', actual='{actual_value}'")

def test_legacy_transformer():
    """Test the legacy transformer using the new system."""
    print("\n=== TESTING LEGACY TRANSFORMER (NEW SYSTEM) ===")

    mock_result = create_mock_answers_result()

    # Transform using legacy transformer (now powered by configuration)
    transformed = AnswersTransformer.transform_to_reference_format(mock_result)

    print("Legacy transformer result (configuration-driven):")
    print(json.dumps(transformed, indent=2, default=str))

def test_factory():
    """Test the DataTransformerFactory."""
    print("\n=== TESTING DATA TRANSFORMER FACTORY ===")

    mock_result = create_mock_answers_result()

    # Test factory transformation
    transformed = DataTransformerFactory.transform_result("Answers", mock_result)

    print("Factory transformation result:")
    print(json.dumps(transformed, indent=2, default=str))

    # Test unknown table (should fall back to configurable transformer)
    mock_unknown = {
        "source_table": "UnknownTable",
        "data": "test",
        "id": 123
    }

    unknown_transformed = DataTransformerFactory.transform_result("UnknownTable", mock_unknown)
    print(f"\nUnknown table transformation (should be unchanged): {unknown_transformed == mock_unknown}")

def test_performance_comparison():
    """Compare performance between old and new approaches."""
    print("\n=== PERFORMANCE COMPARISON ===")
    import time

    mock_result = create_mock_answers_result()
    num_iterations = 1000

    # Test configurable transformer performance
    transformer = ConfigurableTransformer()
    start_time = time.time()
    for _ in range(num_iterations):
        transformer.transform("Answers", mock_result)
    config_time = time.time() - start_time

    print(f"Configurable transformer: {config_time:.4f}s for {num_iterations} transformations")
    print(f"Average per transformation: {(config_time/num_iterations)*1000:.2f}ms")

if __name__ == "__main__":
    try:
        test_mapping_repository()
        test_configurable_transformer()
        test_legacy_transformer()
        test_factory()
        test_performance_comparison()
        print("\n=== ALL TESTS COMPLETED ===")
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
