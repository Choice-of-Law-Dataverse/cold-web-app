# Configuration-Driven Data Transformation System

This system provides a flexible, externalized approach to transforming data between different formats using JSON configuration files.

## Overview

The transformation system consists of several components:

1. **Mapping Repository** (`mapping_repository.py`) - Manages loading and caching of transformation configurations
2. **Configurable Transformer** (`configurable_transformer.py`) - Applies transformations based on external configuration
3. **Transformation Configurations** (`app/mapping/transformations/*.json`) - JSON files defining transformation rules
4. **Legacy Compatibility** (`transformers.py`) - Maintains backward compatibility while using the new system

## How It Works

### 1. Configuration Files

Transformation rules are stored as JSON files in `app/mapping/transformations/`. Each file defines:

- **Direct mappings**: Simple field-to-field mappings
- **Conditional mappings**: Mappings with fallback values
- **Nested mappings**: Transformations for related/nested data
- **Boolean mappings**: Converting boolean values to specific strings
- **Array operations**: Operations on arrays (join, extract, etc.)
- **Post-processing**: Rules for cleaning up the output

### 2. Example Configuration

```json
{
  "table_name": "Answers",
  "description": "Transformation rules for Answers table",
  "version": "1.0",
  "mappings": {
    "direct_mappings": {
      "id": "CoLD_ID",
      "Answer": "Answer"
    },
    "conditional_mappings": {
      "sort_date": {
        "primary": "updated_at",
        "fallback": "result_date"
      }
    },
    "nested_mappings": {
      "related_questions": {
        "source_array": "related_questions",
        "index": 0,
        "mappings": {
          "Question": "Question"
        }
      }
    }
  }
}
```

### 3. Usage in Code

```python
from app.services.transformers import DataTransformerFactory

# Transform using the factory (automatically detects appropriate transformer)
transformed_data = DataTransformerFactory.transform_result("Answers", source_data)

# Or use the configurable transformer directly
from app.services.configurable_transformer import get_configurable_transformer
transformer = get_configurable_transformer()
transformed_data = transformer.transform("Answers", source_data)
```

## Currently Supported Tables

The system currently supports transformations for the following tables:

- **Answers** (`answers_mapping.json`) - Complete transformation for survey answers
- **Court Decisions** (`court_decisions_mapping.json`) - Legal case decisions and citations  
- **Domestic Instruments** (`domestic_instruments_mapping.json`) - National laws and regulations
- **Regional Instruments** (`regional_instruments_mapping.json`) - Regional treaties and agreements
- **Questions** (`questions_mapping.json`) - Survey questions and metadata

Each transformation includes:
- Field mappings between current and reference formats
- Nested data transformations for related records
- Boolean value conversions
- JSON extraction for complex fields
- Array operations for specialist and literature data
- User information mapping
- Post-processing cleanup rules

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

1. Create a new JSON file in `app/mapping/transformations/` named `{table_name}_mapping.json`
2. Define the transformation rules following the schema above
3. The system will automatically load and use the new configuration

## Benefits

- **Externalized Configuration**: Transformation rules are stored outside the code
- **No Code Changes**: Add new transformations by creating JSON files
- **Version Control**: Configuration files can be version controlled
- **Flexible Rules**: Support for complex nested transformations
- **Backward Compatible**: Existing transformers continue to work
- **Performance**: Configurations are cached for efficiency
- **Testable**: Easy to test transformations with mock data

## Testing

Run the test suite to verify the transformation system:

```bash
# Test specific table transformations
python test_answers_mapping.py
python test_court_decisions_transformation.py  
python test_domestic_instruments_transformation.py
python test_regional_instruments_transformation.py

# Test all transformations together
python test_all_transformations.py

# Test the configurable transformer system
python test_configurable_transformers.py
```

This will test:
- Mapping repository functionality
- Configuration-driven transformations
- Legacy transformer compatibility
- Performance benchmarks
