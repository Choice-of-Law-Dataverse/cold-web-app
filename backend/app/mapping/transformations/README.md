# Configuration-Driven Data Transformation System

⚠️ **IMPORTANT UPDATE**: The transformation system has been migrated from JSON files to Python class-based configurations.

## Overview

The transformation system consists of several components:

1. **Mapping Repository** (`mapping_repository.py`) - Manages loading and caching of transformation configurations
2. **Configurable Transformer** (`configurable_transformer.py`) - Applies transformations based on configuration
3. **Transformation Configurations** (`app/mapping/configs/*.py`) - **NEW: Python classes defining transformation rules**
4. **Enum Values** (`app/mapping/enums.py`) - **NEW: Type-safe enums for categorical values**
5. **Legacy Compatibility** (`transformers.py`) - Maintains backward compatibility while using the new system

## Migration from JSON to Python Classes

### What Changed?

All transformation configurations have been migrated from JSON files to Python classes:

**Old (JSON):**
```json
{
  "table_name": "Answers",
  "mappings": {
    "boolean_mappings": {
      "active": {
        "source_field": "is_active",
        "true_value": "Yes",
        "false_value": "No"
      }
    }
  }
}
```

**New (Python):**
```python
from app.schemas.mapping_schema import MappingConfig, Mappings, BooleanMapping
from app.mapping.enums import YesNoValue

ANSWERS_MAPPING = MappingConfig(
    table_name="Answers",
    mappings=Mappings(
        boolean_mappings={
            "active": BooleanMapping(
                source_field="is_active",
                true_value=YesNoValue.YES,
                false_value=YesNoValue.NO,
            )
        }
    )
)
```

### Benefits of Python Classes:
- ✅ **Better type safety** and IDE support (autocomplete, type checking)
- ✅ **Compile-time validation** instead of runtime JSON parsing errors
- ✅ **Cleaner enum usage** for categorical values (Yes/No/None)
- ✅ **Easier to review** changes in version control (better diffs)
- ✅ **No JSON parsing overhead** at runtime
- ✅ **Better refactoring** support (find references, rename symbols)

## How It Works

### 1. Configuration Files

Transformation rules are now stored as Python classes in `app/mapping/configs/`. Each file defines a `MappingConfig` object with:

- **Direct mappings**: Simple field-to-field mappings
- **Conditional mappings**: Mappings with fallback values
- **Nested mappings**: Transformations for related/nested data
- **Boolean mappings**: Converting boolean values to specific strings (now with enums!)
- **Array operations**: Operations on arrays (join, extract, etc.)
- **Post-processing**: Rules for cleaning up the output

### 2. Example Configuration

```python
from app.schemas.mapping_schema import (
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)
from app.mapping.enums import YesNoValue

ANSWERS_MAPPING = MappingConfig(
    table_name="Answers",
    description="Transformation rules for Answers table",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "id": "CoLD_ID",
            "Answer": "Answer",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="updated_at",
                fallback="result_date",
            ),
        },
        nested_mappings={
            "related_questions": NestedMapping(
                source_array="related_questions",
                index=0,
                mappings={
                    "Question": "Question",
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
```

### 3. Usage in Code

```python
from app.services.transformers import DataTransformerFactory

# Transform using the factory (automatically detects appropriate transformer)
transformed_data = DataTransformerFactory.transform_result("Answers", source_data)

# Or use the configurable transformer directly
from app.services.configurable_transformer import ConfigurableTransformer
from app.services.mapping_repository import MappingRepository

transformer = ConfigurableTransformer()
transformed_data = transformer.transform("Answers", source_data)
```

## Currently Supported Tables

The system currently supports transformations for 15 tables:

- **Answers** - Complete transformation for survey answers
- **Arbitral Awards** - Arbitration decisions and awards
- **Arbitral Institutions** - Arbitration organization information
- **Arbitral Provisions** - Arbitration agreement provisions
- **Arbitral Rules** - Arbitration procedural rules
- **Court Decisions** - Legal case decisions and citations
- **Domestic Instruments** - National laws and regulations
- **Domestic Legal Provisions** - Domestic law provisions
- **International Instruments** - International treaties and conventions
- **International Legal Provisions** - International law provisions
- **Jurisdictions** - Country and jurisdiction information
- **Literature** - Academic literature and publications
- **Questions** - Survey questions and metadata
- **Regional Instruments** - Regional treaties and agreements
- **Regional Legal Provisions** - Regional law provisions

All configurations are located in `app/mapping/configs/` as Python modules.

## Enum Values for Categorical Data

The system now uses type-safe enums for categorical values:

```python
from app.mapping.enums import YesNoValue

# Available values:
YesNoValue.YES    # "Yes"
YesNoValue.NO     # "No"
YesNoValue.NONE   # "None"
```

These enums ensure type safety and prevent typos in string values.

## Configuration Reference

### Direct Mappings
Maps source fields directly to target fields:
```json
"direct_mappings": {
  "target_field": "source_field"
}
```

### Conditional Mappings
Maps with fallback values:
```json
"conditional_mappings": {
  "target_field": {
    "primary": "preferred_source_field",
    "fallback": "fallback_source_field"
  }
}
```

### Nested Mappings
Handles transformations of nested/related data:
```json
"nested_mappings": {
  "mapping_name": {
    "source_array": "related_items",
    "index": 0,
    "mappings": {
      "target_field": "source_field"
    },
    "boolean_mappings": {
      "target_bool_field": {
        "source_field": "source_bool_field",
        "true_value": "Yes",
        "false_value": "No"
      }
    },
    "array_operations": {
      "target_joined_field": {
        "operation": "join",
        "field": "field_to_join",
        "separator": ", "
      }
    }
  }
}
```

### Boolean Mappings
Converts boolean values to specific output formats:
```json
"boolean_mappings": {
  "target_bool_field": {
    "source_field": "source_bool_field",
    "true_value": "Yes",
    "false_value": "No"
  }
}
```

### Complex Mappings
Handles advanced transformations like JSON extraction and array operations:
```json
"complex_mappings": {
  "target_field": {
    "source_field": "source_array_field",
    "type": "array_extract",
    "operation": "join_ids"
  }
}
```

Supported operations:
- `join_ids`: Extract numeric IDs and join with commas
- `join_record_ids`: Extract record IDs and join with commas  
- `join_display_values`: Create display values in format "PREFIX-ID"
- `first_item_as_airtable_format`: Convert first JSON array item to Airtable format

### Post Processing
Cleanup rules applied after transformation:
```json
"post_processing": {
  "remove_null_values": true,
  "remove_empty_strings": false
}
```

## Adding New Transformations

1. Create a new Python file in `app/mapping/configs/` named `{table_name}_mapping.py`
2. Define the transformation rules using Pydantic models:

```python
from app.schemas.mapping_schema import MappingConfig, Mappings
from app.mapping.enums import YesNoValue

NEW_TABLE_MAPPING = MappingConfig(
    table_name="New Table",
    description="Transformation rules for New Table",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "id": "CoLD_ID",
            # Add more mappings...
        },
    ),
)
```

3. Import and register it in `app/mapping/configs/__init__.py`:

```python
from .new_table_mapping import NEW_TABLE_MAPPING

ALL_MAPPINGS = {
    # ... existing mappings ...
    "New Table": NEW_TABLE_MAPPING,
}
```

4. The system will automatically load and use the new configuration

## Benefits

- **Type Safety**: IDE autocomplete and type checking for all mappings
- **Compile-Time Validation**: Pydantic validates configurations at import time
- **Enum Support**: Type-safe enums for categorical values (Yes/No/None)
- **Better Refactoring**: Find references and rename symbols across the codebase
- **Version Control**: Better diffs and easier code reviews
- **No Runtime Parsing**: No JSON parsing overhead
- **Testable**: Easy to test transformations with mock data
- **Backward Compatible**: Existing transformers continue to work

## Legacy JSON Files

⚠️ The JSON files in this directory (`*.json`) are **DEPRECATED** and no longer loaded by the application.

They are kept for reference only. All active configurations are in `app/mapping/configs/`.

## Testing

Run the test suite to verify the transformation system:

```bash
# Test mapping schemas and validation
pytest tests/test_mapping_schema.py

# Test mapping repository
pytest tests/test_mapping_repository_validation.py

# Test enum support
pytest tests/test_mapping_enums.py

# Test the configurable transformer system
pytest tests/test_configurable_transformers.py

# Test all transformations together
pytest tests/test_all_transformations.py
```

This will test:
- Mapping repository functionality
- Configuration-driven transformations
- Enum value handling
- Legacy transformer compatibility
- Performance benchmarks
