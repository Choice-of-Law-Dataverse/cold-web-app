#!/usr/bin/env python3
"""
Test script for Regional Instruments transformation.
"""

import json
import sys
import os

# Add the current directory to the Python path to import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.services.transformers import DataTransformerFactory
from app.services.configurable_transformer import ConfigurableTransformer

def create_mock_regional_instrument_result():
    """Create a mock regional instrument result for testing."""
    return {
        "source_table": "Regional Instruments",
        "id": 1,
        "rank": 1,
        "result_date": None,
        "URL": None,
        "Date": None,
        "Title": "Regulation (EC) No 593/2008 of the European Parliament and of the Council of 17 June 2008 on the law applicable to contractual obligations",
        "CoLD_ID": "RI-Rom-5",
        "Created": "2025-02-18T11:59:00",
        "nc_order": 1,
        "ID_Number": 5,
        "Attachment": None,
        "created_at": "2025-06-10T15:13:41",
        "created_by": "usaf3dew23c77lgf",
        "ncRecordId": "rec0kcLxvV6YKZ6Ps",
        "updated_at": None,
        "updated_by": None,
        "Abbreviation": "Rome I",
        "ncRecordHash": "488cd770c46db2d89020cab842c241e22bc77186",
        "related_specialists": [
            {
                "id": 3,
                "Created": "2025-02-18T10:09:00",
                "nc_order": 14,
                "Specialist": "Thomas Kadner Graziano",
                "created_at": "2025-06-10T15:21:22",
                "created_by": "usaf3dew23c77lgf",
                "ncRecordId": "rec9NgsWJL9wKaBbM",
                "updated_at": None,
                "updated_by": None,
                "ncRecordHash": "ac79439c82c39f868684446e54f30e559dcb57c3"
            },
            {
                "id": 16,
                "Created": "2025-02-18T10:09:00",
                "nc_order": 57,
                "Specialist": "Geert Van Calster",
                "created_at": "2025-06-10T15:21:22",
                "created_by": "usaf3dew23c77lgf",
                "ncRecordId": "recrC4s7HWnDfVFqT",
                "updated_at": None,
                "updated_by": None,
                "ncRecordHash": "53c5330aa02dacec12e1e3a89d3aca5269fd7621"
            },
            {
                "id": 6,
                "Created": "2025-02-18T10:09:00",
                "nc_order": 4,
                "Specialist": "Francisco Garcimartín Alférez",
                "created_at": "2025-06-10T15:21:22",
                "created_by": "usaf3dew23c77lgf",
                "ncRecordId": "rec4O4ZiKrVlfKOoi",
                "updated_at": "2025-07-25T14:17:50",
                "updated_by": "usgiwnmibb0sw46o",
                "ncRecordHash": "cea9dcedd3ad71246dddb0ea22a8efb47e5f5b0d"
            }
        ]
    }

def load_reference_data():
    """Load the reference data for comparison."""
    try:
        with open('app/mapping/regional_instruments_reference.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Reference file not found")
        return None

def test_regional_instruments_transformation():
    """Test Regional Instruments transformation."""
    print("=== TESTING REGIONAL INSTRUMENTS TRANSFORMATION ===")
    
    mock_result = create_mock_regional_instrument_result()
    
    # Transform using the factory
    transformed = DataTransformerFactory.transform_result("Regional Instruments", mock_result)
    
    print("Transformed Regional Instrument:")
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
            'Title',
            'Abbreviation',
            'ID Number',
            'Specialists',
            'Specialists Link'
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
    mock_result = create_mock_regional_instrument_result()
    
    # Check if Regional Instruments mapping is loaded
    if transformer.mapping_repo.has_mapping("Regional Instruments"):
        print("✓ Regional Instruments mapping found")
        
        # Transform
        transformed = transformer.transform("Regional Instruments", mock_result)
        
        print(f"Transformed result has {len(transformed)} fields")
        
        # Check some key transformations
        expected_checks = [
            ("id", "RI-Rom-5"),
            ("Title", "Regulation (EC) No 593/2008 of the European Parliament and of the Council of 17 June 2008 on the law applicable to contractual obligations"),
            ("Abbreviation", "Rome I"),
            ("ID Number", 5)
        ]
        
        print("\n=== SPECIFIC FIELD CHECKS ===")
        for field, expected in expected_checks:
            actual = transformed.get(field)
            status = "✓" if actual == expected else "✗"
            print(f"{status} {field}: expected='{expected}', actual='{actual}'")
            
    else:
        print("✗ Regional Instruments mapping not found")

def test_array_operations():
    """Test array operations for specialists."""
    print("\n=== TESTING ARRAY OPERATIONS ===")
    
    transformer = ConfigurableTransformer()
    
    # Test data with specialists array
    test_data = {
        "related_specialists": [
            {
                "id": 3,
                "Specialist": "Thomas Kadner Graziano",
                "ncRecordId": "rec9NgsWJL9wKaBbM"
            },
            {
                "id": 16,
                "Specialist": "Geert Van Calster",
                "ncRecordId": "recrC4s7HWnDfVFqT"
            },
            {
                "id": 6,
                "Specialist": "Francisco Garcimartín Alférez",
                "ncRecordId": "rec4O4ZiKrVlfKOoi"
            }
        ]
    }
    
    # Apply array operations
    transformed = {}
    transformer._apply_array_operations(
        test_data["related_specialists"],
        transformed,
        {
            "Specialists": {
                "operation": "join",
                "field": "Specialist",
                "separator": ","
            },
            "Specialists Link": {
                "operation": "join", 
                "field": "ncRecordId",
                "separator": ","
            }
        }
    )
    
    print("Array operations results:")
    for key, value in transformed.items():
        print(f"  {key}: {value}")

def test_complex_mappings():
    """Test complex mappings for array extraction."""
    print("\n=== TESTING COMPLEX MAPPINGS ===")
    
    transformer = ConfigurableTransformer()
    
    # Test data with complex fields
    test_data = {
        "Literature_Link": [
            {"id": 283, "ncRecordId": "recABC123"},
            {"id": 49, "ncRecordId": "recDEF456"}
        ],
        "Regional_Legal_Provisions_Link": [
            {"id": 1, "ncRecordId": "recXYZ789"},
            {"id": 2, "ncRecordId": "recPQR012"}
        ]
    }
    
    # Apply complex mapping
    transformed = {}
    transformer._apply_complex_mappings(
        test_data, 
        transformed, 
        {
            "Literature": {
                "source_field": "Literature_Link",
                "type": "array_extract",
                "operation": "join_ids"
            },
            "Literature Link": {
                "source_field": "Literature_Link",
                "type": "array_extract",
                "operation": "join_record_ids"
            },
            "Regional Legal Provisions": {
                "source_field": "Regional_Legal_Provisions_Link",
                "type": "array_extract",
                "operation": "join_display_values"
            }
        }
    )
    
    print("Complex mapping results:")
    for key, value in transformed.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    try:
        test_regional_instruments_transformation()
        test_configurable_transformer_direct()
        test_array_operations()
        test_complex_mappings()
        print("\n=== ALL REGIONAL INSTRUMENTS TESTS COMPLETED ===")
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
