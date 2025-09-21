#!/usr/bin/env python3
"""
Simple test to see what the actual NocoDB API returns for Domestic Instruments
without needing full backend dependencies.
"""
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_nocodb_response():
    """Check what NocoDB actually returns."""

    try:
        # Try to mock minimal config
        from unittest.mock import Mock

        import app.config as config_module
        config_module.config = Mock()
        config_module.config.NOCODB_BASE_URL = "your-nocodb-url"
        config_module.config.NOCODB_API_TOKEN = "your-token"

        from app.services.nocodb import NocoDBService

        # Create NocoDBService instance
        nocodb = NocoDBService(
            base_url=config_module.config.NOCODB_BASE_URL,
            api_token=config_module.config.NOCODB_API_TOKEN
        )

        print("=== Testing NocoDB Response ===")
        print("This will make a real API call to NocoDB...")

        # Get first few rows from Domestic Instruments table
        rows = nocodb.list_rows("Domestic Instruments", limit=3)

        print(f"Number of rows returned: {len(rows)}")

        if rows:
            first_row = rows[0]
            print(f"First row keys: {sorted(first_row.keys())}")

            # Look for boolean fields
            boolean_fields = {}
            for key, value in first_row.items():
                if isinstance(value, bool) or "Compatible" in key:
                    boolean_fields[key] = value

            print(f"Boolean/Compatible fields: {boolean_fields}")

            # Print full first row for inspection
            print("Full first row:")
            for key, value in sorted(first_row.items()):
                print(f"  {key}: {value} (type: {type(value)})")

        else:
            print("No rows returned from NocoDB!")

    except ImportError as e:
        print(f"Import error: {e}")
        print("This test requires the actual NocoDB configuration.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("This test requires real NocoDB credentials.")
    print("You would need to configure the actual NOCODB_BASE_URL and NOCODB_API_TOKEN.")
    print("Instead, let's check what the mapping expects vs what might be returned...")

    # Let's check the mapping expectations
    try:
        from app.services.configurable_transformer import get_configurable_transformer

        transformer = get_configurable_transformer()
        reverse_mapping = transformer.get_reverse_field_mapping("Domestic Instruments")

        print("\n=== Expected Boolean Fields ===")
        for target, source in reverse_mapping.items():
            if "Compatible" in target or "Compatible" in source:
                print(f"  Frontend expects: '{target}'")
                print(f"  Maps to backend: '{source}'")

        # Get the mapping config directly
        mapping_repo = transformer.mapping_repo
        config = mapping_repo.get_mapping("Domestic Instruments")
        if not config:
            print("No mapping configuration found for Domestic Instruments.")
        else:
            boolean_mappings = config.get("mappings", {}).get("boolean_mappings", {})

            print("\n=== Boolean Mapping Configuration ===")
            for target_field, boolean_config in boolean_mappings.items():
                source_field = boolean_config.get("source_field")
                print(f"  '{target_field}' <- '{source_field}'")
                print(f"    Expected in NocoDB data: '{source_field}'")

    except Exception as e:
        print(f"Error checking mappings: {e}")
