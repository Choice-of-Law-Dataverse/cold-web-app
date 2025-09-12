#!/usr/bin/env python3
"""
Test script for Domestic Instruments transformation.
"""

import json
import sys
import os

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.transformers import DataTransformerFactory
from app.services.configurable_transformer import ConfigurableTransformer

def create_mock_domestic_instrument_result():
    """Create a mock domestic instrument result for testing."""
    return {
        "source_table": "Domestic Instruments",
        "id": 126,
        "rank": 1,
        "result_date": "1967-01-01",
        "Date": "1967",
        "Status": "In force",
        "CoLD_ID": "DI-TCD-29",
        "Created": "2021-10-04T09:57:00",
        "nc_order": 4,
        "ID_Number": 29,
        "created_at": "2025-06-10T15:10:55",
        "created_by": "usaf3dew23c77lgf",
        "ncRecordId": "rec2OZtzxtU3fGARi",
        "updated_at": "2025-07-25T12:44:05",
        "updated_by": "usgiwnmibb0sw46o",
        "Abbreviation": None,
        "Source__PDF_": None,
        "Source__URL_": None,
        "ncRecordHash": "74f130a0772a6a14b4a5e2a213d3d4b5c776987b",
        "Official_Title": "Ordinance No 6 of 21 March 1967",
        "Entry_Into_Force": None,
        "Publication_Date": None,
        "related_questions": None,
        "Title__in_English_": "Chadian Law on the Reform of Judicial Organisation",
        "Relevant_Provisions": "Arts 70-72",
        "related_jurisdictions": [
            {
                "id": 173,
                "Done": None,
                "Name": "Chad",
                "Type": "State",
                "Region": "Africa",
                "Created": "2021-03-07T14:24:00",
                "nc_order": 173,
                "created_at": "2025-06-10T15:08:23",
                "created_by": "usaf3dew23c77lgf",
                "ncRecordId": "reck2QOyHDrSYtAc0",
                "updated_at": None,
                "updated_by": None,
                "Irrelevant_": None,
                "Alpha_3_Code": "TCD",
                "Legal_Family": "Civil Law",
                "ncRecordHash": "14e9f64b4837a106db5b8848e5210f1b6ad8a9b1",
                "North_South_Divide": "Global South",
                "Jurisdiction_Summary": None,
                "Jurisdictional_Differentiator": None
            }
        ],
        "related_legal_provisions": None,
        "Jurisdictions_Alpha_3_Code": "TCD",
        "Full_Text_of_the_Provisions": None,
        "Compatible_With_the_HCCH_Principles_": False,
        "Compatible_With_the_UNCITRAL_Model_Law_": None
    }

def load_reference_data():
    """Load the reference data for comparison."""
    try:
        with open('app/mapping/domestic_instruments_reference.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Reference file not found")
        return None

def test_domestic_instruments_transformation():
    """Test Domestic Instruments transformation."""
    print("=== TESTING DOMESTIC INSTRUMENTS TRANSFORMATION ===")
    
    mock_result = create_mock_domestic_instrument_result()
    
    # Transform using the factory
    transformed = DataTransformerFactory.transform_result("Domestic Instruments", mock_result)
    
    print("Transformed Domestic Instrument:")
    print(json.dumps(transformed, indent=2, default=str))
    
    # Load reference for comparison
    reference_data = load_reference_data()
    if reference_data and reference_data.get('results'):
        reference_result = reference_data['results'][0]
        
        print("\n=== FIELD COMPARISON ===")
        reference_keys = set(reference_result.keys())
        transformed_keys = set(transformed.keys())
        
        print(f"Reference keys: {len(reference_keys)}")
        print(f"Transformed keys: {len(transformed_keys)}")
        print(f"Missing keys: {reference_keys - transformed_keys}")
        print(f"Extra keys: {transformed_keys - reference_keys}")
        
        # Check specific important mappings
        key_mappings_to_check = [
            'id',
            'ID',
            'Title (in English)',
            'Jurisdictions',
            'Jurisdictions Alpha-3 Code',
            'Type (from Jurisdictions)',
            'Relevant Provisions',
            'Date',
            'Status'
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
    mock_result = create_mock_domestic_instrument_result()
    
    # Check if Domestic Instruments mapping is loaded
    if transformer.mapping_repo.has_mapping("Domestic Instruments"):
        print("✓ Domestic Instruments mapping found")
        
        # Transform
        transformed = transformer.transform("Domestic Instruments", mock_result)
        
        print(f"Transformed result has {len(transformed)} fields")
        
        # Check some key transformations
        expected_checks = [
            ("id", "DI-TCD-29"),
            ("Title (in English)", "Chadian Law on the Reform of Judicial Organisation"),
            ("Jurisdictions", "Chad"),
            ("Jurisdictions Alpha-3 Code", "TCD"),
            ("Type (from Jurisdictions)", "State"),
            ("Date", "1967"),
            ("Status", "In force")
        ]
        
        print("\n=== SPECIFIC FIELD CHECKS ===")
        for field, expected in expected_checks:
            actual = transformed.get(field)
            status = "✓" if actual == expected else "✗"
            print(f"{status} {field}: expected='{expected}', actual='{actual}'")
            
    else:
        print("✗ Domestic Instruments mapping not found")

def test_boolean_mappings():
    """Test boolean field mappings."""
    print("\n=== TESTING BOOLEAN MAPPINGS ===")
    
    transformer = ConfigurableTransformer()
    
    # Test data with boolean fields
    test_data = {
        "Compatible_With_the_HCCH_Principles_": False,
        "Compatible_With_the_UNCITRAL_Model_Law_": None
    }
    
    # Apply boolean mapping
    transformed = {}
    transformer._apply_boolean_mappings(
        test_data, 
        transformed, 
        {
            "Compatible With the HCCH Principles": {
                "source_field": "Compatible_With_the_HCCH_Principles_",
                "true_value": True,
                "false_value": False
            },
            "Compatible With the UNCITRAL Model Law": {
                "source_field": "Compatible_With_the_UNCITRAL_Model_Law_",
                "true_value": True,
                "false_value": False
            }
        }
    )
    
    print("Boolean mapping results:")
    for key, value in transformed.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")

def test_conditional_mappings():
    """Test conditional field mappings."""
    print("\n=== TESTING CONDITIONAL MAPPINGS ===")
    
    transformer = ConfigurableTransformer()
    
    # Test data with conditional fields
    test_data = {
        "Title__in_English_": "Chadian Law on the Reform of Judicial Organisation",
        "Official_Title": "Ordinance No 6 of 21 March 1967",
        "Source__URL_": None,
        "Official_Source_URL": "https://example.com/law.pdf"
    }
    
    # Apply conditional mapping
    transformed = {}
    transformer._apply_conditional_mappings(
        test_data, 
        transformed, 
        {
            "Title (in English)": {
                "primary": "Title__in_English_",
                "fallback": "Official_Title"
            },
            "Source (URL)": {
                "primary": "Source__URL_",
                "fallback": "Official_Source_URL"
            }
        }
    )
    
    print("Conditional mapping results:")
    for key, value in transformed.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    try:
        test_domestic_instruments_transformation()
        test_configurable_transformer_direct()
        test_boolean_mappings()
        test_conditional_mappings()
        print("\n=== ALL DOMESTIC INSTRUMENTS TESTS COMPLETED ===")
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
