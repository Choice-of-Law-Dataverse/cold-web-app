# Migration Guide: Python Class-based Mappings

## Overview

The mapping system has been refactored from JSON files to Python class-based configurations. This guide explains the changes and migration path.

## What Changed

### Before (JSON-based)
- Mappings stored in `app/mapping/transformations/*.json`
- Loaded and parsed at runtime
- String values for categorical data (e.g., "Yes", "No")
- Runtime validation errors

### After (Python-based)
- Mappings stored in `app/mapping/configs/*.py`
- Loaded as Python modules (import time)
- Enum values for categorical data (e.g., `BooleanValue.YES`)
- Compile-time validation via Pydantic

## File Structure

```
backend/app/mapping/
├── configs/                    # NEW: Python class-based configurations
│   ├── __init__.py            # Registry of all mappings
│   ├── answers_mapping.py     # Answers table mapping
│   ├── court_decisions_mapping.py
│   ├── jurisdictions_mapping.py
│   └── ... (15 total)
├── enums.py                   # NEW: Enum definitions
└── transformations/           # DEPRECATED: Legacy JSON files
    ├── README.md              # Updated documentation
    ├── answers_mapping.json   # DEPRECATED
    └── ... (kept for reference)
```

## Code Changes

### MappingRepository

**Old:**
```python
# Loaded from JSON files
repo = MappingRepository(mappings_directory="path/to/json/files")
```

**New:**
```python
# Loads from Python classes by default
repo = MappingRepository()

# Or with custom mappings dict
from app.mapping.configs import ALL_MAPPINGS
repo = MappingRepository(mappings_dict=ALL_MAPPINGS)
```

### ConfigurableTransformer

No changes required - the transformer works the same way:

```python
from app.services.configurable_transformer import ConfigurableTransformer

transformer = ConfigurableTransformer()
result = transformer.transform("Answers", source_data)
```

### Using Enums

**Old (string values):**
```json
{
  "boolean_mappings": {
    "active": {
      "source_field": "is_active",
      "true_value": "Yes",
      "false_value": "No"
    }
  }
}
```

**New (enum values):**
```python
from app.mapping.enums import BooleanValue

BooleanMapping(
    source_field="is_active",
    true_value=BooleanValue.YES,  # Type-safe enum
    false_value=BooleanValue.NO,
)
```

## Benefits

### 1. Type Safety
IDEs can now provide autocomplete and type checking:
```python
# IDE knows the structure
mapping.mappings.direct_mappings["id"]  # Autocomplete works!
mapping.mappings.boolean_mappings["active"].true_value  # Type checked!
```

### 2. Compile-Time Validation
Errors are caught at import time, not runtime:
```python
# Old: Runtime error when JSON is loaded
# New: Import error if configuration is invalid
```

### 3. Better Refactoring
Find all usages and rename symbols safely:
```python
# Find all references to ANSWERS_MAPPING
from app.mapping.configs import ANSWERS_MAPPING
```

### 4. Version Control
Better diffs in Git:
```diff
# Old JSON diff - hard to read
-  "true_value": "Yes"
+  "true_value": "yes"

# New Python diff - clearer intent
-  true_value=BooleanValue.YES,
+  true_value=BooleanValue.NO,
```

### 5. No Runtime Overhead
No JSON parsing at runtime:
```python
# Old: JSON file read + parse on every load
# New: Python module imported once
```

## Testing Impact

### Test Updates

Tests that used `mappings_directory` parameter need updating:

**Old:**
```python
repo = MappingRepository(mappings_directory=temp_dir)
```

**New:**
```python
test_mappings = {
    "TestTable": MappingConfig(...)
}
repo = MappingRepository(mappings_dict=test_mappings)
```

See `tests/test_mapping_repository_validation.py` for examples.

### New Tests

Added comprehensive enum tests:
- `tests/test_mapping_enums.py` - Tests enum values and their usage

All existing tests continue to pass with the new system.

## Backward Compatibility

### Legacy JSON Support

JSON files are no longer loaded but are kept for reference. If needed for external tools, they can be regenerated from Python classes.

### Migration Script

A conversion script was used for the initial migration:
```bash
python /tmp/convert_mappings.py
```

This script can be used if you need to convert additional JSON mappings to Python.

## Adding New Mappings

### Step 1: Create Python Module

Create `app/mapping/configs/new_table_mapping.py`:

```python
from app.schemas.mapping_schema import MappingConfig, Mappings
from app.mapping.enums import BooleanValue

NEW_TABLE_MAPPING = MappingConfig(
    table_name="New Table",
    description="Description",
    version="1.0",
    mappings=Mappings(
        direct_mappings={"id": "CoLD_ID"},
    ),
)
```

### Step 2: Register in __init__.py

Add to `app/mapping/configs/__init__.py`:

```python
from .new_table_mapping import NEW_TABLE_MAPPING

ALL_MAPPINGS = {
    # ... existing mappings ...
    "New Table": NEW_TABLE_MAPPING,
}

__all__ = [
    # ... existing exports ...
    "NEW_TABLE_MAPPING",
]
```

### Step 3: Test

```python
from app.mapping.configs import NEW_TABLE_MAPPING

assert NEW_TABLE_MAPPING.table_name == "New Table"
```

## Common Patterns

### Using Enums for Boolean Values

```python
from app.mapping.enums import BooleanValue

# String-based enum (inherits from str)
BooleanValue.YES == "Yes"  # True
```

### Direct Mappings

```python
direct_mappings={
    "target_field": "source_field",
    "id": "CoLD_ID",
}
```

### Conditional Mappings

```python
from app.schemas.mapping_schema import ConditionalMapping

conditional_mappings={
    "sort_date": ConditionalMapping(
        primary="updated_at",
        fallback="created_at",
    ),
}
```

### Nested Mappings with Enums

```python
from app.schemas.mapping_schema import NestedMapping, BooleanMapping
from app.mapping.enums import BooleanValue

nested_mappings={
    "related_items": NestedMapping(
        source_array="items",
        index=0,
        boolean_mappings={
            "active": BooleanMapping(
                source_field="is_active",
                true_value=BooleanValue.YES,
                false_value=BooleanValue.NONE,
            ),
        },
    ),
}
```

## Troubleshooting

### Import Errors

If you get import errors, ensure Python modules are properly structured:

```python
# All modules must be importable
from app.mapping.configs import ALL_MAPPINGS  # Should work

# Check individual mappings
from app.mapping.configs import ANSWERS_MAPPING  # Should work
```

### Missing Mappings

If a mapping is not found:

1. Check it's registered in `__init__.py`
2. Verify the table name matches exactly
3. Check for import errors in the module

### Pydantic Validation Errors

If you get Pydantic validation errors at import time:

1. Check required fields are provided
2. Verify enum values are correct
3. Ensure nested structures are complete

## Future Enhancements

Potential improvements to consider:

1. **More Enums**: Add enums for other categorical fields
2. **Validation Rules**: Add custom validators for domain-specific rules
3. **Type Hints**: Add more specific type hints for better IDE support
4. **Documentation**: Generate API documentation from Pydantic models
5. **Migration Tools**: Tools to validate mappings or generate test data

## Questions?

For questions or issues with the migration, please:
1. Check this guide and the README
2. Review test files for examples
3. Open an issue with details of the problem
