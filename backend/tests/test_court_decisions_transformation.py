#!/usr/bin/env python3
# ruff: noqa: E501
"""
Test script for Court Decisions transformation.
"""

import json
import os
import sys

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.configurable_transformer import ConfigurableTransformer
from app.services.transformers import DataTransformerFactory


def create_mock_court_decision_result():
    """Create a mock court decision result for testing."""
    return {
        "source_table": "Court Decisions",
        "id": 123,
        "rank": 1.6372154,
        "result_date": "2007-01-01",
        "CoLD_ID": "CD-GBR-1167",
        "Case_Citation": "Halpern v Halpern (Nos 1 and 2) [2007] EWCA Civ 291",
        "Case_Title": "Halpern v Halpern",
        "Instance": "Court of Appeal",
        "Date": "2007",
        "Abstract": "The case handles a dispute over a compromise agreement in an inheritance matter. The claimants, the son and grandson of a deceased rabbi sought to enforce a compromise reached with their siblings through arbitration before a Beth Din in Zurich.",
        "Created": "2021-03-07T14:55:35.000Z",
        "ncRecordId": "recjlaRwXh9WKWFND",
        "ID_number": 1167,
        "updated_at": "2025-03-27T11:46:35.000Z",
        "updated_by": "usrou8psfCtFIsSG5",
        "created_by": "usreXYOAyNX5GCVQe",
        "Publication_Date_ISO": "2007-01-01",
        "Questions": "09-FoC,05-PA,05.1-PA,11-FoC",
        "Answers_Link": "recBKrsOEnRZ83GaM,reckx9WhLonvWH2Nq,recbArBTzobwHjezU,recyqLu3YN7XObpsg",
        "Answers_Question": 'Are the parties allowed to choose non-State law ("rules of law") to govern their contract?,Are the parties allowed to choose different laws for different parts or aspects of the contract? ,Are the parties allowed to choose the applicable law with respect to only one part or aspect of their contract?,Are the parties allowed to incorporate rules of law into their contract by way of reference? ',
        "Official_Source__URL_": "https://www.bailii.org/ew/cases/EWCA/Civ/2007/291.html",
        "Official_Source__PDF_": '[{"id":"at62votknyfmgei1","url":"https://coldnocodb.1744e88118d6dbb785a27b3f7431a798.r2.cloudflarestorage.com/nc/uploads/noco/p1q5x3pj29vkrdr/mdmls7kc3a3w1vu/ciw1ko4kixrlep0/CD-GBR-1167_9OMja.pdf","title":"CD-GBR-1167.pdf","mimetype":"application/pdf","size":185262,"icon":"mdi-pdf-box"}]',
        "related_jurisdictions": [
            {
                "id": 241,
                "Done": True,
                "Name": "United Kingdom",
                "Type": "State",
                "Region": "Europe",
                "Created": "2021-03-07T14:24:00",
                "nc_order": 241,
                "created_at": "2025-06-10T15:08:28",
                "created_by": "usaf3dew23c77lgf",
                "ncRecordId": "recyBIItDtNAH3Sgq",
                "updated_at": "2025-07-24T16:15:00",
                "updated_by": "usgiwnmibb0sw46o",
                "Irrelevant_": None,
                "Alpha_3_Code": "GBR",
                "Legal_Family": "Common Law",
                "ncRecordHash": "cda63756546f266ddcca5a92876810cc0935033b",
                "North_South_Divide": "Global North",
            }
        ],
        "related_themes": [
            {"id": 1, "Theme": "Party autonomy", "Created": "2025-03-21T08:57:00"},
            {"id": 2, "Theme": "Rules of law", "Created": "2025-03-21T08:57:00"},
            {"id": 3, "Theme": "Freedom of choice", "Created": "2025-03-21T08:57:00"},
        ],
        "Jurisdictions_Alpha_3_Code": "GBR",
        "Text_of_the_Relevant_Legal_Provisions": "Preamble UK Contracts (Applicable Law) Act 1990...",
    }


def load_reference_data():
    """Load the reference data for comparison."""
    try:
        with open("app/mapping/court_decisions_reference.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Reference file not found")
        return None


def test_court_decisions_transformation():
    """Test Court Decisions transformation."""
    print("=== TESTING COURT DECISIONS TRANSFORMATION ===")

    mock_result = create_mock_court_decision_result()

    # Transform using the factory
    transformed = DataTransformerFactory.transform_result("Court Decisions", mock_result)

    print("Transformed Court Decision:")
    print(json.dumps(transformed, indent=2, default=str))

    # Load reference for comparison
    reference_data = load_reference_data()
    if reference_data and reference_data.get("results"):
        reference_result = reference_data["results"][0]

        print("\n=== FIELD COMPARISON ===")
        reference_keys = set(reference_result.keys())
        transformed_keys = set(transformed.keys())

        print(f"Reference keys: {len(reference_keys)}")
        print(f"Transformed keys: {len(transformed_keys)}")
        print(f"Missing keys: {reference_keys - transformed_keys}")
        print(f"Extra keys: {transformed_keys - reference_keys}")

        # Check specific important mappings
        key_mappings_to_check = [
            "id",
            "ID",
            "Case Citation",
            "Case Title",
            "Jurisdictions",
            "Jurisdictions Alpha-3 Code",
            "Region (from Jurisdictions)",
            "Themes",
            "Official Source (URL)",
            "Publication Date ISO",
        ]

        print("\n=== KEY FIELD VERIFICATION ===")
        for key in key_mappings_to_check:
            ref_val = reference_result.get(key)
            trans_val = transformed.get(key)
            status = "✓" if trans_val == ref_val else "✗"
            print(f"{status} {key}: expected='{ref_val}', actual='{trans_val}'")


def test_configurable_transformer_direct():
    """Test the configurable transformer directly."""
    print("\n=== TESTING CONFIGURABLE TRANSFORMER DIRECTLY ===")

    transformer = ConfigurableTransformer()
    mock_result = create_mock_court_decision_result()

    # Check if Court Decisions mapping is loaded
    if transformer.mapping_repo.has_mapping("Court Decisions"):
        print("✓ Court Decisions mapping found")

        # Transform
        transformed = transformer.transform("Court Decisions", mock_result)

        print(f"Transformed result has {len(transformed)} fields")

        # Check some key transformations
        expected_checks = [
            ("id", "CD-GBR-1167"),
            ("Case Citation", "Halpern v Halpern (Nos 1 and 2) [2007] EWCA Civ 291"),
            ("Jurisdictions", "United Kingdom"),
            ("Jurisdictions Alpha-3 Code", "GBR"),
        ]

        print("\n=== SPECIFIC FIELD CHECKS ===")
        for field, expected in expected_checks:
            actual = transformed.get(field)
            status = "✓" if actual == expected else "✗"
            print(f"{status} {field}: {actual}")

    else:
        print("✗ Court Decisions mapping not found")


def test_json_extraction():
    """Test JSON extraction for PDF fields."""
    print("\n=== TESTING JSON EXTRACTION ===")

    transformer = ConfigurableTransformer()

    # Test data with JSON PDF field
    test_data = {
        "Official_Source__PDF_": '[{"id":"at62votknyfmgei1","url":"https://example.com/file.pdf","title":"test.pdf","mimetype":"application/pdf","size":185262}]'
    }

    # Apply complex mapping
    transformed = {}
    transformer._apply_complex_mappings(
        test_data,
        transformed,
        {
            "Official Source (PDF)": {
                "source_field": "Official_Source__PDF_",
                "type": "json_extract",
                "operation": "first_item_as_airtable_format",
            }
        },
    )

    print(f"JSON extraction result: {transformed.get('Official Source (PDF)')}")


if __name__ == "__main__":
    try:
        test_court_decisions_transformation()
        test_configurable_transformer_direct()
        test_json_extraction()
        print("\n=== ALL COURT DECISIONS TESTS COMPLETED ===")
    except Exception as e:
        print(f"Test error: {e}")
        import traceback

        traceback.print_exc()
