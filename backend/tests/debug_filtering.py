#!/usr/bin/env python3
import json
import os
import sys

from app.services.configurable_transformer import get_configurable_transformer

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


class MockFilter:
    def __init__(self, column, value):
        self.column = column
        self.value = value


def debug_filtering_process():
    """Debug the complete filtering process step by step."""

    print("=== Debugging Filtering Process ===")

    # Mock NocoDB data that matches the ACTUAL structure we found
    mock_rows = [
        {
            "Id": 1,
            "CoLD ID": "DOM-001",
            "Title (in English)": "HCCH Compatible Instrument",
            "Compatible With the HCCH Principles?": True,
            "Compatible With the UNCITRAL Model Law?": False,
            "Date": "2024",
            "Status": "Active",
        },
        {
            "Id": 2,
            "CoLD ID": "DOM-002",
            "Title (in English)": "UNCITRAL Compatible Instrument",
            "Compatible With the HCCH Principles?": False,
            "Compatible With the UNCITRAL Model Law?": True,
            "Date": "2023",
            "Status": "Active",
        },
        {
            "Id": 3,
            "CoLD ID": "DOM-003",
            "Title (in English)": "Both Compatible Instrument",
            "Compatible With the HCCH Principles?": True,
            "Compatible With the UNCITRAL Model Law?": True,
            "Date": "2022",
            "Status": "Draft",
        },
    ]

    # Frontend request
    filters = [MockFilter("Compatible With the HCCH Principles?", True)]
    table = "Domestic Instruments"

    print(f"Table: {table}")
    print(f"Filter: column='{filters[0].column}', value={filters[0].value}")
    print(f"Number of mock rows: {len(mock_rows)}")

    # Get reverse mapping
    transformer = get_configurable_transformer()
    reverse_mapping = transformer.get_reverse_field_mapping(table)

    print(f"\nReverse mapping loaded: {len(reverse_mapping)} mappings")

    # Simulate the filtering process
    results = []
    for i, raw in enumerate(mock_rows):
        print(f"\n--- Processing Row {i + 1} ---")
        print(f"Raw data keys: {list(raw.keys())}")

        # The search.py logic: ensure each row is a dict
        if isinstance(raw, str):
            try:
                row = json.loads(raw)
            except Exception:
                print("  Skipped: Failed to parse JSON")
                continue
        elif isinstance(raw, dict):
            row = raw
        else:
            print("  Skipped: Not dict or string")
            continue

        print(f"Row data: {row}")

        match = True
        for filter_item in filters:
            column = filter_item.column
            value = filter_item.value

            print(f"  Applying filter: {column} = {value}")

            # Try to reverse-map the column name from transformed name to source name
            source_column = reverse_mapping.get(column, column)
            print(f"    Initial mapping: '{column}' -> '{source_column}'")

            # Also try with question mark suffix removed (for boolean fields)
            if source_column == column and column.endswith("?"):
                source_column_without_q = column[:-1]
                source_column = reverse_mapping.get(source_column_without_q, column)
                print(
                    f"    After '?' removal: '{source_column_without_q}' -> '{source_column}'"
                )

            print(f"    Final source column: '{source_column}'")

            cell = row.get(source_column)
            print(f"    Cell value: {cell} (type: {type(cell)})")

            if cell is None:
                print("    ❌ Cell is None - no match")
                match = False
                break

            # Check if it's a list (should not be for boolean fields)
            if isinstance(cell, list):
                print("    Cell is a list - checking list elements")
                # ... list handling logic ...
                continue

            # Scalar field matching
            if isinstance(value, str):
                if not isinstance(cell, str) or value.lower() not in cell.lower():
                    print(f"    ❌ String match failed: '{value}' not in '{cell}'")
                    match = False
                    break
                else:
                    print(f"    ✅ String match: '{value}' found in '{cell}'")
            elif isinstance(value, (int, float, bool)):
                if cell != value:
                    print(f"    ❌ Value match failed: {cell} != {value}")
                    match = False
                    break
                else:
                    print(f"    ✅ Value match: {cell} == {value}")
            else:
                print(f"    ❌ Unsupported filter type: {type(value)}")
                raise ValueError(
                    f"Unsupported filter type for column {column}: {value}"
                )

        if match:
            print(f"  ✅ Row {i + 1} MATCHES")
            results.append(row)
        else:
            print(f"  ❌ Row {i + 1} does not match")

    print("\n=== Final Results ===")
    print(f"Matching rows: {len(results)}")
    for i, result in enumerate(results):
        print(
            f"  Result {i + 1}: {result.get('CoLD ID')} - {result.get('Title (in English)')}"
        )

    return results


if __name__ == "__main__":
    debug_filtering_process()
