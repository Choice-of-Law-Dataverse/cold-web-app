#!/usr/bin/env python3
import os
import sys

from app.services.transformers import DataTransformerFactory

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


def test_frontend_field_requirements():
    """Test that the transformation includes all fields required by the frontend."""

    # Sample record structure from actual NocoDB data (combining multiple sources)
    test_record = {
        "source_table": "Domestic Instruments",
        "id": 135,
        "cold_id": "DI-URY-168",
        "Id": 135,
        "CoLD ID": "DI-URY-168",
        "Title (in English)": "Uruguayan General Act on Private International Law",
        "Compatible With the HCCH Principles?": True,
        "Compatible With the UNCITRAL Model Law?": False,
        "Date": "2020",
        "Entry Into Force": None,
        "Jurisdictions": ["Uruguay"],
        "Jurisdictions Alpha-3 Code": ["URY"],
        "Type (from Jurisdictions)": ["State"],
        "_nc_m2m_Jurisdictions_Domestic_Instrus": [
            {
                "ncRecordId": "rec123",
                "Alpha-3 Code": "URY",
                "Name": "Uruguay",
                "Type": "State",
            }
        ],
    }

    print("=== Testing Frontend Field Requirements ===")
    print("Frontend expects these fields:")
    print("- instrument.ID (for route)")
    print("- instrument['Jurisdictions Alpha-3 Code'] (for flag)")
    print("- instrument['Entry Into Force'] or instrument['Date'] (for date)")
    print("- instrument['Title (in English)'] (for title)")

    # Transform the record
    transformed = DataTransformerFactory.transform_result(
        "Domestic Instruments", test_record
    )

    print("\n=== Transformation Results ===")
    print(f"Transformed keys: {sorted(transformed.keys())}")

    # Check each required field
    required_fields = [
        "ID",
        "Jurisdictions Alpha-3 Code",
        "Entry Into Force",
        "Date",
        "Title (in English)",
    ]

    print("\n=== Required Field Check ===")
    for field in required_fields:
        if field in transformed:
            print(f"✅ {field}: {transformed[field]}")
        else:
            print(f"❌ {field}: MISSING")

    # Show all fields for debugging
    print("\n=== All Transformed Fields ===")
    for key, value in sorted(transformed.items()):
        print(f"  {key}: {repr(value)}")

    # Test the sorting logic the frontend uses
    print("\n=== Sorting Test ===")
    date_value = transformed.get("Date")
    if date_value:
        try:
            numeric_date = Number(date_value)  # JavaScript Number()
            print(f"Date '{date_value}' converts to number: {numeric_date}")
        except Exception:
            try:
                numeric_date = int(date_value)
                print(f"Date '{date_value}' converts to int: {numeric_date}")
            except Exception:
                print(f"❌ Date '{date_value}' cannot be converted to number")

    return transformed


def Number(value):
    """Simulate JavaScript Number() conversion."""
    if value is None:
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return float("nan")
    return float("nan")


if __name__ == "__main__":
    test_frontend_field_requirements()
