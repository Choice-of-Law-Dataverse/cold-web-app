#!/usr/bin/env python3
import logging
import os
import sys

from app.services.configurable_transformer import get_configurable_transformer

logger = logging.getLogger(__name__)

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


def debug_reverse_mapping():
    """Debug the reverse mapping to see what's happening."""

    logger.debug("=== Debugging Reverse Mapping ===")

    transformer = get_configurable_transformer()
    reverse_mapping = transformer.get_reverse_field_mapping("Domestic Instruments")

    logger.debug("Full reverse mapping:")
    for key, value in sorted(reverse_mapping.items()):
        logger.debug(f"'{key}' -> '{value}'")

    # Test the specific field the frontend is sending
    frontend_field = "Compatible With the HCCH Principles?"
    logger.debug(f"\nTesting frontend field: '{frontend_field}'")

    # Test direct lookup
    source_column = reverse_mapping.get(frontend_field, frontend_field)
    logger.debug(f"Direct lookup: '{frontend_field}' -> '{source_column}'")

    # Test with question mark removed
    if source_column == frontend_field and frontend_field.endswith("?"):
        source_column_without_q = frontend_field[:-1]
        source_column = reverse_mapping.get(source_column_without_q, frontend_field)
        logger.debug(f"Without '?': '{source_column_without_q}' -> '{source_column}'")

    logger.debug(f"Final mapping: '{frontend_field}' -> '{source_column}'")

    # Check if the expected backend field exists
    expected_backend_field = "Compatible_With_the_HCCH_Principles_"
    if source_column == expected_backend_field:
        logger.debug("✅ Mapping is correct!")
    else:
        logger.debug(f"❌ Expected '{expected_backend_field}' but got '{source_column}'")

    # Check what backend fields are in the reverse mapping
    logger.debug("\nBackend fields containing 'Compatible':")
    for target, source in reverse_mapping.items():
        if "Compatible" in target or "Compatible" in source:
            logger.debug(f"'{target}' -> '{source}'")


if __name__ == "__main__":
    debug_reverse_mapping()
