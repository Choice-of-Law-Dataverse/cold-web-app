"""Tests for mapping enums and their usage in configurations."""

import pytest

from app.mapping.enums import BooleanValue
from app.schemas.mapping_schema import BooleanMapping, MappingConfig, Mappings


def test_boolean_value_enum():
    """Test BooleanValue enum."""
    assert BooleanValue.YES == "Yes"
    assert BooleanValue.NO == "No"
    assert BooleanValue.NONE == "None"
    
    # Enums should be comparable to strings
    assert BooleanValue.YES == "Yes"
    assert BooleanValue.YES.value == "Yes"


def test_boolean_mapping_with_enums():
    """Test that BooleanMapping works with enum values."""
    mapping = BooleanMapping(
        source_field="is_active",
        true_value=BooleanValue.YES,
        false_value=BooleanValue.NO,
    )
    
    assert mapping.source_field == "is_active"
    assert mapping.true_value == "Yes"  # Enum inherits from str
    assert mapping.false_value == "No"


def test_mapping_config_with_enum_boolean_mappings():
    """Test complete mapping config with enum-based boolean mappings."""
    config = MappingConfig(
        table_name="Test Table",
        description="Test mapping with enums",
        version="1.0",
        mappings=Mappings(
            direct_mappings={"id": "CoLD_ID"},
            boolean_mappings={
                "active": BooleanMapping(
                    source_field="is_active",
                    true_value=BooleanValue.YES,
                    false_value=BooleanValue.NONE,
                ),
            },
        ),
    )
    
    assert config.mappings.boolean_mappings["active"].true_value == "Yes"
    assert config.mappings.boolean_mappings["active"].false_value == "None"


def test_enum_in_actual_mapping():
    """Test that enum values are used in actual mapping configurations."""
    from app.mapping.configs import ANSWERS_MAPPING
    
    # Check that the Answers mapping loads successfully
    assert ANSWERS_MAPPING.table_name == "Answers"
    
    # Check nested boolean mapping uses enum
    nested_mapping = ANSWERS_MAPPING.mappings.nested_mappings.get("related_jurisdictions")
    assert nested_mapping is not None
    assert nested_mapping.boolean_mappings is not None
    
    irrelevant_mapping = nested_mapping.boolean_mappings.get("Jurisdictions Irrelevant")
    assert irrelevant_mapping is not None
    assert irrelevant_mapping.true_value == "Yes"
    assert irrelevant_mapping.false_value == "None"


def test_jurisdictions_mapping_boolean_enum():
    """Test that Jurisdictions mapping uses boolean true/false correctly."""
    from app.mapping.configs import JURISDICTIONS_MAPPING
    
    assert JURISDICTIONS_MAPPING.table_name == "Jurisdictions"
    
    # Check boolean mappings use native booleans
    irrelevant_mapping = JURISDICTIONS_MAPPING.mappings.boolean_mappings.get("Irrelevant?")
    assert irrelevant_mapping is not None
    assert irrelevant_mapping.true_value is True
    assert irrelevant_mapping.false_value is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
