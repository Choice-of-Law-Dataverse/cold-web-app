# Pydantic Mapping Validation

This document describes the Pydantic validation enhancement for mapping JSON files.

## Overview

All mapping JSON files in `app/mapping/transformations/` are now validated using Pydantic models, providing:
- Type safety and IDE autocomplete
- Configuration error detection at startup
- Detailed validation error messages
- Self-documenting schema

## Schema Structure

The mapping schema is defined in `app/schemas/mapping_schema.py` with the following models:

### MappingConfig
The root model for a mapping configuration file.

```python
from app.schemas import MappingConfig

# Load and validate a mapping
mapping = MappingConfig(
    table_name="Court Decisions",
    description="Mapping for Court Decisions",
    version="1.0",
    mappings={
        "direct_mappings": {
            "id": "CoLD_ID",
            "Case Title": "Case_Title",
        },
        "conditional_mappings": {
            "sort_date": {
                "primary": "Publication_Date_ISO",
                "fallback": "updated_at",
            },
        },
    },
)
```

### Component Models

- **ConditionalMapping**: Field mapping with primary/fallback
- **BooleanMapping**: Boolean field transformations
- **ArrayOperation**: Array operations (join, etc.)
- **NestedMapping**: Nested/related data mappings
- **ComplexMapping**: Complex transformations
- **UserMapping**: User data transformations
- **PostProcessing**: Post-processing operations

## Using the MappingRepository

### With Validation (Default)

```python
from app.services.mapping_repository import get_mapping_repository

# Get the repository (validates all files on load)
repo = get_mapping_repository()

# Get a validated mapping
mapping = repo.get_mapping("Court Decisions")

if isinstance(mapping, MappingConfig):
    # Type-safe access with IDE autocomplete
    table_name = mapping.table_name
    direct_maps = mapping.mappings.direct_mappings
    
    # Access nested mappings with type safety
    if "related_jurisdictions" in mapping.mappings.nested_mappings:
        nested = mapping.mappings.nested_mappings["related_jurisdictions"]
        source_array = nested.source_array
```

### Without Validation (Backward Compatible)

```python
from app.services.mapping_repository import MappingRepository

# Disable validation for backward compatibility
repo = MappingRepository(validate=False)

# Get mapping as raw dict
mapping = repo.get_mapping("Court Decisions")
# mapping is dict[str, Any]
```

## Validation Benefits

### Before: Runtime Errors

```python
# Load raw JSON - no validation
mapping = json.load(open("mapping.json"))

# Typo or missing field only discovered at runtime
direct_mappings = mapping["mapings"]["direct_mappings"]  # KeyError!
```

### After: Startup Validation

```python
# Validation happens at startup
repo = get_mapping_repository()
# If any mapping file has errors, you get a detailed message:
# ValidationError: 2 validation errors for MappingConfig
#   version: Field required
#   mappings.direct_mappings: Field required
```

## IDE Support

With Pydantic models, your IDE can provide:

```python
mapping = repo.get_mapping("Court Decisions")

# IDE knows mapping is MappingConfig and shows:
mapping.table_name          # ✓ string
mapping.description         # ✓ string
mapping.version             # ✓ string
mapping.mappings.           # ✓ Shows: direct_mappings, conditional_mappings, etc.
```

## Creating New Mappings

When creating new mapping files, use the schema as a guide:

```json
{
  "table_name": "My New Table",
  "description": "Description of the mapping",
  "version": "1.0",
  "mappings": {
    "direct_mappings": {
      "target_field": "source_field"
    },
    "conditional_mappings": {
      "field_name": {
        "primary": "primary_source",
        "fallback": "fallback_source"
      }
    },
    "nested_mappings": {
      "related_items": {
        "source_array": "items",
        "array_operations": {
          "Items": {
            "operation": "join",
            "field": "name",
            "separator": ", "
          }
        }
      }
    }
  }
}
```

## Validation Errors

If a mapping file has errors, you'll see detailed messages:

```
ERROR: Validation error in mapping file court_decisions_mapping.json:
2 validation errors for MappingConfig
version
  Field required [type=missing]
mappings.conditional_mappings.sort_date.primary
  Field required [type=missing]
```

## Testing

Tests are provided in:
- `tests/test_mapping_schema.py` - Schema validation tests
- `tests/test_mapping_repository_validation.py` - Repository integration tests

Run tests:
```bash
uv run pytest tests/test_mapping_schema.py -v
uv run pytest tests/test_mapping_repository_validation.py -v
```

## Migration Guide

Existing code using `MappingRepository` continues to work without changes. To leverage type safety:

### Before
```python
mapping = repo.get_mapping("Court Decisions")
# mapping: dict[str, Any] | None
direct_maps = mapping["mappings"]["direct_mappings"]  # type: Any
```

### After (with type checking)
```python
mapping = repo.get_mapping("Court Decisions")
# mapping: MappingConfig | dict[str, Any] | None

if isinstance(mapping, MappingConfig):
    # Full type safety and IDE support
    direct_maps = mapping.mappings.direct_mappings  # type: dict[str, str]
```

## Disabling Validation

If you encounter issues or want to disable validation temporarily:

```python
from app.services.mapping_repository import MappingRepository

# Create repository without validation
repo = MappingRepository(validate=False)

# All mappings load as dict[str, Any] without validation
```

## Future Enhancements

Possible future improvements:
- Add custom validators for specific mapping patterns
- Generate JSON schema for external tools
- Add runtime validation in transformers
- Create validation CLI tool for mapping files

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- Source: `app/schemas/mapping_schema.py`
- Tests: `tests/test_mapping_schema.py`, `tests/test_mapping_repository_validation.py`
