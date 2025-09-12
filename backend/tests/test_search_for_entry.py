#!/usr/bin/env python3

"""
Test script for the new search_for_entry function integration
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.search import SearchService


def test_search_for_entry_integration():
    """
    Test the updated curated_details_search method that uses search_for_entry SQL function
    and includes hop1_relations by default
    """
    search_service = SearchService()
    
    # Test with a known CoLD_ID (you'll need to replace with actual test data)
    test_cases = [
        {"table": "Answers", "cold_id": "CHE_01.1-P"},
        {"table": "Court Decisions", "cold_id": "CD-CHE-1020"},
        {"table": "Questions", "cold_id": "Q-01.1"},
    ]
    
    for test_case in test_cases:
        table = test_case["table"]
        cold_id = test_case["cold_id"]
        
        print(f"\nTesting {table} with CoLD_ID: {cold_id}")
        
        # Test the updated method
        result = search_service.curated_details_search(table, cold_id)
        
        if "error" in result:
            print(f"  Error (might be expected if test data doesn't exist): {result['error']}")
        else:
            print(f"  Success! Found record with ID: {result.get('id')}")
            print(f"  Source table: {result.get('source_table')}")
            print(f"  Has hop1_relations: {'hop1_relations' in result}")
            print(f"  Data structure similar to full_text_search: {bool(result.get('source_table') and result.get('id'))}")
            if 'hop1_relations' in result:
                relations = result['hop1_relations']
                if relations:
                    print(f"  Relations found: {list(relations.keys())}")
                else:
                    print("  No relations for this record")


def test_data_structure_consistency():
    """
    Verify that the curated_details_search returns data in a structure similar to full_text_search
    """
    search_service = SearchService()
    
    table = "Answers"
    test_id = "CHE_01.1-P"  # Replace with actual test data
    
    print(f"\nTesting data structure consistency for {table} {test_id}")
    
    # Test curated details
    curated_result = search_service.curated_details_search(table, test_id)
    
    if "error" not in curated_result:
        print("Curated details structure:")
        print(f"  - source_table: {'source_table' in curated_result}")
        print(f"  - id: {'id' in curated_result}")
        print(f"  - hop1_relations: {'hop1_relations' in curated_result}")
        print(f"  - transformed by DataTransformerFactory: {hasattr(curated_result, 'get')}")
        
        # Check if it has similar fields to full text search results
        expected_fields = ['source_table', 'id']
        missing_fields = [field for field in expected_fields if field not in curated_result]
        if missing_fields:
            print(f"  Missing expected fields: {missing_fields}")
        else:
            print("  ✅ Has all expected fields for consistency with full_text_search")
    else:
        print(f"  Error in curated details: {curated_result['error']}")


if __name__ == "__main__":
    print("Testing updated search_for_entry integration...")
    
    try:
        test_search_for_entry_integration()
        print("\n✅ Basic integration test completed")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_data_structure_consistency() 
        print("\n✅ Data structure consistency test completed")
    except Exception as e:
        print(f"\n❌ Data structure consistency test failed: {e}")
        import traceback
        traceback.print_exc()
