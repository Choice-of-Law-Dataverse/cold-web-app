#!/usr/bin/env python3
"""
Simple test for the transformers module.
"""

import json
import os
import sys

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

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
            {"id": 4, "Theme": "Consumer contracts", "Created": "2025-03-21T08:57:00"},
            {
                "id": 15,
                "Theme": "Employment contracts",
                "Created": "2025-03-21T08:57:00",
            },
        ],
        "More_Information": None,
        "Question_CoLD_ID": "34-FV",
        "related_questions": [
            {
                "id": 30,
                "Created": "2023-11-27T13:03:00",
                "Question": "Is further guidance on applicable law in international contracts providing protection to weaker parties necessary?",  # noqa: E501
                "nc_order": 1,
                "Theme_Code": "Rev",
                "created_at": "2025-06-10T15:08:37",
                "ncRecordId": "rec0XQRyxFGp9he5X",
                "Primary_Theme": "FV",
                "Question_Number": "34",
                "Answering_Options": "Yes, No, No strong opinions",
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
                "North_South_Divide": "Global South",
            }
        ],
        "Jurisdictions_Alpha_3_Code": "ABW",
    }


def test_answers_transformer():
    """Test the AnswersTransformer directly."""
    print("=== TESTING ANSWERS TRANSFORMER ===")

    mock_result = create_mock_answers_result()
    transformed = AnswersTransformer.transform_to_reference_format(mock_result)

    print("Original result keys:", sorted(mock_result.keys()))
    print("Transformed result keys:", sorted(transformed.keys()))
    print("\nTransformed result:")
    print(json.dumps(transformed, indent=2, default=str))

    # Check key mappings
    expected_mappings = {
        "source_table": "Answers",
        "id": "ABW_34-FV",
        "ID": "ABW_34-FV",
        "Answer": "No data",
        "Jurisdictions": "Aruba",
        "Jurisdictions Alpha-3 code": "ABW",
        "Question": "Is further guidance on applicable law in international contracts providing protection to weaker parties necessary?",  # noqa: E501
        "Questions Theme Code": "FV",
        "Themes": "Consumer contracts, Employment contracts",
    }

    print("\n=== KEY MAPPING VERIFICATION ===")
    for key, expected_value in expected_mappings.items():
        actual_value = transformed.get(key)
        status = "✓" if actual_value == expected_value else "✗"
        print(f"{status} {key}: expected='{expected_value}', actual='{actual_value}'")


def test_factory():
    """Test the DataTransformerFactory."""
    print("\n=== TESTING DATA TRANSFORMER FACTORY ===")

    # Test getting transformer for Answers
    answers_transformer = DataTransformerFactory.get_transformer("Answers")
    print(f"Answers transformer: {answers_transformer}")

    # Test getting transformer for non-existent table
    unknown_transformer = DataTransformerFactory.get_transformer("UnknownTable")
    print(f"Unknown table transformer: {unknown_transformer}")

    # Test transform_result method
    mock_result = create_mock_answers_result()

    # Transform Answers result
    transformed_answers = DataTransformerFactory.transform_result("Answers", mock_result)
    print(f"Transformed Answers result has {len(transformed_answers)} fields")

    # Transform unknown table result (should return original)
    mock_unknown = {"source_table": "UnknownTable", "data": "test"}
    transformed_unknown = DataTransformerFactory.transform_result("UnknownTable", mock_unknown)
    print(f"Unknown table result unchanged: {transformed_unknown == mock_unknown}")


if __name__ == "__main__":
    test_answers_transformer()
    test_factory()
