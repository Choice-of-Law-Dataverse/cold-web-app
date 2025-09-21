#!/usr/bin/env python3
import logging
import os
import sys

from app.services.transformers import DataTransformerFactory

logger = logging.getLogger(__name__)

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

    logger.debug("=== Testing Frontend Field Requirements ===")
    logger.debug("Frontend expects these fields:")
    logger.debug("- instrument.ID (for route)")
    logger.debug("- instrument['Jurisdictions Alpha-3 Code'] (for flag)")
    logger.debug("- instrument['Entry Into Force'] or instrument['Date'] (for date)")
    logger.debug("- instrument['Title (in English)'] (for title)")

    # Transform the record
    transformed = DataTransformerFactory.transform_result("Domestic Instruments", test_record)

    logger.debug("\n=== Transformation Results ===")
    logger.debug(f"Transformed keys: {sorted(transformed.keys())}")

    # Check each required field
    required_fields = [
        "ID",
        "Jurisdictions Alpha-3 Code",
        "Entry Into Force",
        "Date",
        "Title (in English)",
    ]

    logger.debug("\n=== Required Field Check ===")
    for field in required_fields:
        if field in transformed:
            logger.debug(f"✅ {field}: {transformed[field]}")
        else:
            logger.debug(f"❌ {field}: MISSING")

    # Show all fields for debugging
    logger.debug("\n=== All Transformed Fields ===")
    for key, value in sorted(transformed.items()):
        logger.debug(f"{key}: {repr(value)}")

    # Test the sorting logic the frontend uses
    logger.debug("\n=== Sorting Test ===")
    date_value = transformed.get("Date")
    if date_value:
        try:
            numeric_date = Number(date_value)  # JavaScript Number()
            logger.debug(f"Date '{date_value}' converts to number: {numeric_date}")
        except Exception:
            try:
                numeric_date = int(date_value)
                logger.debug(f"Date '{date_value}' converts to int: {numeric_date}")
            except Exception:
                logger.debug(f"❌ Date '{date_value}' cannot be converted to number")

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
