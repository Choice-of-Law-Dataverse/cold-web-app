#!/usr/bin/env python3
"""
Test script to verify the answers mapping transformation.
"""

import json
import os
import sys

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.transformers import AnswersTransformer


def load_test_data():
    """Load test data from the mapping files."""
    with open("app/mapping/answers_current.json") as f:
        current_data = json.load(f)

    with open("app/mapping/answers_reference.json") as f:
        reference_data = json.load(f)

    return current_data, reference_data


def test_transformation():
    """Test the transformation logic."""
    current_data, reference_data = load_test_data()

    # Get the first result from current data
    current_result = current_data["results"][0]
    reference_result = reference_data["results"][0]

    # Apply transformation using the new transformer
    transformed_result = AnswersTransformer.transform_to_reference_format(current_result)

    print("=== CURRENT RESULT ===")
    print(json.dumps(current_result, indent=2, default=str))

    print("\n=== REFERENCE RESULT ===")
    print(json.dumps(reference_result, indent=2, default=str))

    print("\n=== TRANSFORMED RESULT ===")
    print(json.dumps(transformed_result, indent=2, default=str))

    # Compare key fields
    print("\n=== FIELD COMPARISON ===")
    reference_keys = set(reference_result.keys())
    transformed_keys = set(transformed_result.keys())

    print(f"Reference keys: {sorted(reference_keys)}")
    print(f"Transformed keys: {sorted(transformed_keys)}")
    print(f"Missing keys: {reference_keys - transformed_keys}")
    print(f"Extra keys: {transformed_keys - reference_keys}")

    # Check specific mappings
    mappings_to_check = [
        ("id", "ID"),
        ("source_table", "source_table"),
        ("Answer", "Answer"),
        ("Created", "Created"),
    ]

    print("\n=== SPECIFIC FIELD MAPPINGS ===")
    for ref_field, trans_field in mappings_to_check:
        ref_val = reference_result.get(ref_field)
        trans_val = transformed_result.get(trans_field)
        print(f"{ref_field} -> {trans_field}: '{ref_val}' vs '{trans_val}'")


def create_mock_result():
    """Create a mock result for testing without requiring database connection."""
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


def test_transformation_mock():
    """Test the transformation logic with mock data."""
    try:
        # Get mock data
        current_result = create_mock_result()

        # Apply transformation using the new transformer
        transformed_result = AnswersTransformer.transform_to_reference_format(current_result)

        print("=== TRANSFORMED RESULT ===")
        print(json.dumps(transformed_result, indent=2, default=str))

        # Expected reference structure sample
        expected_keys = {
            "source_table",
            "id",
            "rank",
            "sort_date",
            "ID",
            "Question Link",
            "Jurisdictions Link",
            "Question",
            "Questions Theme Code",
            "Jurisdictions Alpha-3 code",
            "Jurisdictions",
            "Answer",
            "Record ID",
            "Created",
            "Themes",
            "Last Modified",
            "Jurisdictions Region",
            "Jurisdictions Irrelevant",
            "Number",
            "Last Modified By.id",
            "Created By.id",
        }

        transformed_keys = set(transformed_result.keys())

        print(f"\nExpected keys: {sorted(expected_keys)}")
        print(f"Transformed keys: {sorted(transformed_keys)}")
        print(f"Missing keys: {expected_keys - transformed_keys}")
        print(f"Extra keys: {transformed_keys - expected_keys}")

        return transformed_result

    except Exception as e:
        print(f"Error during transformation test: {e}")
        return None


if __name__ == "__main__":
    try:
        test_transformation()
    except Exception as e:
        print(f"Database connection error, running with mock data: {e}")
        test_transformation_mock()
