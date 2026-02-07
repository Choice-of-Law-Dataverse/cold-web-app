#!/usr/bin/env python3
import json
import logging
import os
import sys

from app.services.configurable_transformer import get_configurable_transformer

logger = logging.getLogger(__name__)

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


class MockFilter:
    def __init__(self, column, value):
        self.column = column
        self.value = value


def debug_filtering_process():
    """Debug the complete filtering process step by step."""

    logger.debug("=== Debugging Filtering Process ===")

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

    logger.debug(f"Table: {table}")
    logger.debug(f"Filter: column='{filters[0].column}', value={filters[0].value}")
    logger.debug(f"Number of mock rows: {len(mock_rows)}")

    # Get reverse mapping
    transformer = get_configurable_transformer()
    reverse_mapping = transformer.get_reverse_field_mapping(table)

    logger.debug(f"\nReverse mapping loaded: {len(reverse_mapping)} mappings")

    # Simulate the filtering process
    results = []
    for i, raw in enumerate(mock_rows):
        logger.debug(f"\n--- Processing Row {i + 1} ---")
        logger.debug(f"Raw data keys: {list(raw.keys())}")

        # The search.py logic: ensure each row is a dict
        if isinstance(raw, str):
            try:
                row = json.loads(raw)
            except Exception:
                logger.debug("  Skipped: Failed to parse JSON")
                continue
        elif isinstance(raw, dict):
            row = raw
        else:
            logger.debug("  Skipped: Not dict or string")
            continue

        logger.debug(f"Row data: {row}")

        match = True
        for filter_item in filters:
            column = filter_item.column
            value = filter_item.value

            logger.debug(f"Applying filter: {column} = {value}")

            # Try to reverse-map the column name from transformed name to source name
            source_column = reverse_mapping.get(column, column)
            logger.debug(f"Initial mapping: '{column}' -> '{source_column}'")

            # Also try with question mark suffix removed (for boolean fields)
            if source_column == column and column.endswith("?"):
                source_column_without_q = column[:-1]
                source_column = reverse_mapping.get(source_column_without_q, column)
                logger.debug(f"After '?' removal: '{source_column_without_q}' -> '{source_column}'")

            logger.debug(f"Final source column: '{source_column}'")

            cell = row.get(source_column)
            logger.debug(f"Cell value: {cell} (type: {type(cell)})")

            if cell is None:
                logger.debug("    ❌ Cell is None - no match")
                match = False
                break

            # Check if it's a list (should not be for boolean fields)
            if isinstance(cell, list):
                logger.debug("    Cell is a list - checking list elements")
                # ... list handling logic ...
                continue

            # Scalar field matching
            if isinstance(value, str):
                if not isinstance(cell, str) or value.lower() not in cell.lower():
                    logger.debug(f"❌ String match failed: '{value}' not in '{cell}'")
                    match = False
                    break
                else:
                    logger.debug(f"✅ String match: '{value}' found in '{cell}'")
            elif isinstance(value, (int, float, bool)):
                if cell != value:
                    logger.debug(f"❌ Value match failed: {cell} != {value}")
                    match = False
                    break
                else:
                    logger.debug(f"✅ Value match: {cell} == {value}")
            else:
                logger.debug(f"❌ Unsupported filter type: {type(value)}")
                raise ValueError(f"Unsupported filter type for column {column}: {value}")

        if match:
            logger.debug(f"✅ Row {i + 1} MATCHES")
            results.append(row)
        else:
            logger.debug(f"❌ Row {i + 1} does not match")

    logger.debug("\n=== Final Results ===")
    logger.debug(f"Matching rows: {len(results)}")
    for i, result in enumerate(results):
        logger.debug(f"Result {i + 1}: {result.get('CoLD ID')} - {result.get('Title (in English)')}")

    return results


if __name__ == "__main__":
    debug_filtering_process()
