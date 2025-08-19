#!/usr/bin/env python3
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.services.configurable_transformer import get_configurable_transformer

def debug_reverse_mapping():
    """Debug the reverse mapping to see what's happening."""
    
    print("=== Debugging Reverse Mapping ===")
    
    transformer = get_configurable_transformer()
    reverse_mapping = transformer.get_reverse_field_mapping('Domestic Instruments')
    
    print("Full reverse mapping:")
    for key, value in sorted(reverse_mapping.items()):
        print(f"  '{key}' -> '{value}'")
    
    # Test the specific field the frontend is sending
    frontend_field = "Compatible With the HCCH Principles?"
    print(f"\nTesting frontend field: '{frontend_field}'")
    
    # Test direct lookup
    source_column = reverse_mapping.get(frontend_field, frontend_field)
    print(f"Direct lookup: '{frontend_field}' -> '{source_column}'")
    
    # Test with question mark removed
    if source_column == frontend_field and frontend_field.endswith('?'):
        source_column_without_q = frontend_field[:-1]
        source_column = reverse_mapping.get(source_column_without_q, frontend_field)
        print(f"Without '?': '{source_column_without_q}' -> '{source_column}'")
    
    print(f"Final mapping: '{frontend_field}' -> '{source_column}'")
    
    # Check if the expected backend field exists
    expected_backend_field = "Compatible_With_the_HCCH_Principles_"
    if source_column == expected_backend_field:
        print(f"✅ Mapping is correct!")
    else:
        print(f"❌ Expected '{expected_backend_field}' but got '{source_column}'")
        
    # Check what backend fields are in the reverse mapping
    print(f"\nBackend fields containing 'Compatible':")
    for target, source in reverse_mapping.items():
        if 'Compatible' in target or 'Compatible' in source:
            print(f"  '{target}' -> '{source}'")

if __name__ == "__main__":
    debug_reverse_mapping()
