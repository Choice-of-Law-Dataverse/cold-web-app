#!/usr/bin/env python3
import os
import sys
from app.services.transformers import DataTransformerFactory

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


def test_boolean_transformation():
    """Test that boolean fields are correctly transformed."""

    # Simulate data as it would come from NocoDB after filtering
    test_record = {
        "source_table": "Domestic Instruments",
        "id": 40,
        "cold_id": "DOM-CHN-001",
        "Id": 40,
        "CoLD ID": "DOM-CHN-001",
        "Title (in English)": "Chinese Law on the Laws Applicable to Foreign-Related Civil Relationships",
        "Compatible With the HCCH Principles?": False,  # Actual field name from NocoDB
        "Compatible With the UNCITRAL Model Law?": None,  # Actual field name from NocoDB
        "Date": "2010",
        "Status": "Active",
    }

    print("=== Testing Boolean Transformation ===")
    print(f"Input record keys: {sorted(test_record.keys())}")

    # Apply transformation
    transformed = DataTransformerFactory.transform_result(
        "Domestic Instruments", test_record
    )

    print(f"Output record keys: {sorted(transformed.keys())}")

    # Check for boolean fields
    print("\nBoolean fields in transformed record:")
    found_boolean_fields = False
    for key, value in transformed.items():
        if "Compatible" in key:
            found_boolean_fields = True
            print(f"  {key}: {value} (type: {type(value)})")

    if not found_boolean_fields:
        print("  ❌ No boolean fields found!")
    else:
        print("  ✅ Boolean fields found and transformed!")

    # Check specific fields we expect
    expected_fields = [
        "Compatible With the HCCH Principles",
        "Compatible With the UNCITRAL Model Law",
    ]

    print("\nExpected field verification:")
    for field in expected_fields:
        if field in transformed:
            print(f"  ✅ '{field}': {transformed[field]}")
        else:
            print(f"  ❌ '{field}': MISSING")


if __name__ == "__main__":
    test_boolean_transformation()
