"""Tests for mapping schema validation using Pydantic."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.mapping_schema import (
    ArrayOperation,
    BooleanMapping,
    ComplexMapping,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)


def test_conditional_mapping_valid():
    """Test valid conditional mapping creation."""
    mapping = ConditionalMapping(primary="updated_at", fallback="created_at")
    assert mapping.primary == "updated_at"
    assert mapping.fallback == "created_at"


def test_conditional_mapping_invalid():
    """Test that conditional mapping requires both fields."""
    with pytest.raises(ValidationError):
        ConditionalMapping(primary="updated_at")  # type: ignore


def test_boolean_mapping_valid():
    """Test valid boolean mapping creation."""
    mapping = BooleanMapping(source_field="is_active", true_value="Yes", false_value="No")
    assert mapping.source_field == "is_active"
    assert mapping.true_value == "Yes"
    assert mapping.false_value == "No"


def test_array_operation_valid():
    """Test valid array operation creation."""
    op = ArrayOperation(operation="join", field="name", separator=", ")
    assert op.operation == "join"
    assert op.field == "name"
    assert op.separator == ", "


def test_array_operation_invalid_operation():
    """Test that only 'join' operation is allowed."""
    with pytest.raises(ValidationError):
        ArrayOperation(operation="split", field="name", separator=", ")  # type: ignore


def test_nested_mapping_with_index():
    """Test nested mapping with index extraction."""
    mapping = NestedMapping(
        source_array="related_items",
        index=0,
        mappings={"Item Name": "name", "Item ID": "id"},
        array_operations=None,
        conditional_mappings=None,
        boolean_mappings=None,
    )
    assert mapping.source_array == "related_items"
    assert mapping.index == 0
    assert mapping.mappings == {"Item Name": "name", "Item ID": "id"}


def test_nested_mapping_with_array_operations():
    """Test nested mapping with array operations."""
    mapping = NestedMapping(
        source_array="related_items",
        index=None,
        mappings=None,
        array_operations={
            "Items": ArrayOperation(operation="join", field="name", separator=", "),
        },
        conditional_mappings=None,
        boolean_mappings=None,
    )
    assert mapping.source_array == "related_items"
    assert mapping.array_operations is not None
    assert "Items" in mapping.array_operations
    assert mapping.array_operations["Items"].operation == "join"


def test_complex_mapping_valid():
    """Test valid complex mapping creation."""
    mapping = ComplexMapping(
        source_field="pdf_field",
        type="json_extract",
        operation="first_item_as_airtable_format",
    )
    assert mapping.source_field == "pdf_field"
    assert mapping.type == "json_extract"
    assert mapping.operation == "first_item_as_airtable_format"


def test_user_mapping_valid():
    """Test valid user mapping creation."""
    mapping = UserMapping(
        source_field="updated_by",
        user_fields={
            "Last Modified By.id": "id",
            "Last Modified By.email": "email",
            "Last Modified By.name": "name",
        },
    )
    assert mapping.source_field == "updated_by"
    assert "Last Modified By.id" in mapping.user_fields


def test_mappings_container():
    """Test Mappings container with various mapping types."""
    mappings = Mappings(
        direct_mappings={"id": "CoLD_ID", "name": "Name"},
        conditional_mappings={
            "sort_date": ConditionalMapping(primary="updated_at", fallback="created_at"),
        },
    )
    assert mappings.direct_mappings == {"id": "CoLD_ID", "name": "Name"}
    assert "sort_date" in mappings.conditional_mappings


def test_post_processing_defaults():
    """Test PostProcessing with default values."""
    pp = PostProcessing()
    assert pp.remove_null_values is False
    assert pp.field_transformations == {}


def test_mapping_config_minimal():
    """Test minimal valid MappingConfig."""
    config = MappingConfig(
        table_name="Test Table",
        description="Test mapping",
        version="1.0",
        mappings=Mappings(),
    )
    assert config.table_name == "Test Table"
    assert config.description == "Test mapping"
    assert config.version == "1.0"


def test_mapping_config_complete():
    """Test complete MappingConfig with all fields."""
    config = MappingConfig(
        table_name="Answers",
        description="Transformation rules for Answers",
        version="1.0",
        mappings=Mappings(
            direct_mappings={"id": "CoLD_ID", "Answer": "Answer"},
            conditional_mappings={
                "sort_date": ConditionalMapping(primary="updated_at", fallback="result_date"),
            },
            nested_mappings={
                "related_questions": NestedMapping(
                    source_array="related_questions",
                    index=0,
                    mappings={"Question": "Question"},
                    array_operations=None,
                    conditional_mappings=None,
                    boolean_mappings=None,
                ),
            },
            boolean_mappings={
                "active": BooleanMapping(source_field="is_active", true_value="Yes", false_value="No"),
            },
        ),
        post_processing=PostProcessing(remove_null_values=True),
    )
    assert config.table_name == "Answers"
    assert "sort_date" in config.mappings.conditional_mappings
    assert "related_questions" in config.mappings.nested_mappings
    assert config.post_processing.remove_null_values is True


def test_mapping_config_missing_required():
    """Test that MappingConfig requires all required fields."""
    with pytest.raises(ValidationError):
        MappingConfig(  # type: ignore
            table_name="Test",
            description="Test",
            # missing version and mappings
        )


def test_mapping_config_from_json():
    """Test creating MappingConfig from JSON data."""
    json_data = {
        "table_name": "Court Decisions",
        "description": "Mapping for Court Decisions",
        "version": "1.0",
        "mappings": {
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
    }

    config = MappingConfig(**json_data)
    assert config.table_name == "Court Decisions"
    assert config.mappings.direct_mappings["id"] == "CoLD_ID"
    assert config.mappings.conditional_mappings["sort_date"].primary == "Publication_Date_ISO"


def test_load_actual_mapping_file():
    """Test loading and validating an actual mapping file."""
    # Path to an actual mapping file
    mapping_file = Path(__file__).parent.parent / "app" / "mapping" / "transformations" / "answers_mapping.json"

    if not mapping_file.exists():
        pytest.skip("Mapping file not found")

    with open(mapping_file) as f:
        data = json.load(f)

    # This should validate successfully
    config = MappingConfig(**data)
    assert config.table_name == "Answers"
    assert len(config.mappings.direct_mappings) > 0


def test_nested_mapping_complex_structure():
    """Test nested mapping with all optional fields."""
    mapping = NestedMapping(
        source_array="hop1_relations.related_items",
        index=0,
        mappings={"Item": "name"},
        array_operations={
            "Items List": ArrayOperation(operation="join", field="name", separator=", "),
        },
        conditional_mappings={
            "item_date": ConditionalMapping(primary="created", fallback="updated"),
        },
        boolean_mappings={
            "active": BooleanMapping(source_field="is_active", true_value="Yes", false_value="No"),
        },
    )

    # Add explicit assertions to satisfy type checker
    assert mapping.array_operations is not None
    assert mapping.conditional_mappings is not None
    assert mapping.boolean_mappings is not None

    assert mapping.source_array == "hop1_relations.related_items"
    assert mapping.index == 0
    assert mapping.mappings is not None
    assert mapping.array_operations is not None
    assert mapping.conditional_mappings is not None
    assert mapping.boolean_mappings is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
