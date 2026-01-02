"""Tests for MappingRepository with Pydantic validation."""

import pytest

from app.schemas.mapping_schema import (
    ConditionalMapping,
    MappingConfig,
    Mappings,
    PostProcessing,
)
from app.services.mapping_repository import MappingRepository


@pytest.fixture
def test_mappings_dict():
    """Create a test mappings dictionary."""
    valid_mapping = MappingConfig(
        table_name="TestTable",
        description="Test mapping",
        version="1.0",
        mappings=Mappings(
            direct_mappings={
                "id": "CoLD_ID",
                "name": "Name",
            },
            conditional_mappings={
                "sort_date": ConditionalMapping(
                    primary="updated_at",
                    fallback="created_at",
                ),
            },
        ),
        post_processing=PostProcessing(remove_null_values=True),
    )

    return {
        "TestTable": valid_mapping,
    }


def test_mapping_repository_loads_valid_mappings(test_mappings_dict):
    """Test that MappingRepository loads and validates correct mappings."""
    repo = MappingRepository(mappings_dict=test_mappings_dict)

    # Should have loaded the valid mapping
    mapping = repo.get_mapping("TestTable")
    assert mapping is not None
    assert isinstance(mapping, MappingConfig)
    assert mapping.table_name == "TestTable"
    assert mapping.version == "1.0"


def test_mapping_repository_handles_invalid_mappings():
    """Test that MappingRepository handles missing mappings gracefully."""
    valid_mapping = MappingConfig(
        table_name="ValidTable",
        description="Valid mapping",
        version="1.0",
        mappings=Mappings(
            direct_mappings={"id": "CoLD_ID"},
        ),
    )

    repo = MappingRepository(mappings_dict={"ValidTable": valid_mapping})

    # Valid mapping should be loaded
    assert repo.get_mapping("ValidTable") is not None

    # Non-existent mapping should return None
    assert repo.get_mapping("InvalidTable") is None


def test_mapping_repository_get_all_mappings(test_mappings_dict):
    """Test getting all mappings."""
    repo = MappingRepository(mappings_dict=test_mappings_dict)

    all_mappings = repo.get_all_mappings()
    assert len(all_mappings) >= 1  # At least the valid one
    assert "TestTable" in all_mappings


def test_mapping_repository_has_mapping(test_mappings_dict):
    """Test checking if mapping exists."""
    repo = MappingRepository(mappings_dict=test_mappings_dict)

    assert repo.has_mapping("TestTable") is True
    assert repo.has_mapping("Nonexistent Table") is False


def test_mapping_repository_get_supported_tables(test_mappings_dict):
    """Test getting list of supported tables."""
    repo = MappingRepository(mappings_dict=test_mappings_dict)

    tables = repo.get_supported_tables()
    assert "TestTable" in tables


def test_mapping_repository_with_real_mappings():
    """Test MappingRepository with actual mapping files if they exist."""
    # Use default (loads from configs module)
    repo = MappingRepository()

    # If any mappings exist, they should be loaded
    tables = repo.get_supported_tables()
    if len(tables) > 0:
        # Pick first table and verify it's a MappingConfig
        first_table = tables[0]
        mapping = repo.get_mapping(first_table)
        assert mapping is not None
        assert isinstance(mapping, MappingConfig)
        assert mapping.table_name == first_table


def test_mapping_config_type_safety():
    """Test that validated mappings provide type safety."""
    from app.schemas.mapping_schema import ArrayOperation, NestedMapping

    mapping = MappingConfig(
        table_name="Type Safety Test",
        description="Testing type safety",
        version="1.0",
        mappings=Mappings(
            direct_mappings={
                "id": "CoLD_ID",
            },
            nested_mappings={
                "related_items": NestedMapping(
                    source_array="items",
                    array_operations={
                        "Items": ArrayOperation(
                            operation="join",
                            field="name",
                            separator=", ",
                        ),
                    },
                ),
            },
        ),
    )

    repo = MappingRepository(mappings_dict={"Type Safety Test": mapping})
    loaded_mapping = repo.get_mapping("Type Safety Test")

    assert isinstance(loaded_mapping, MappingConfig)
    # Type checkers can now infer these fields
    assert loaded_mapping.table_name == "Type Safety Test"
    assert "related_items" in loaded_mapping.mappings.nested_mappings
    nested = loaded_mapping.mappings.nested_mappings["related_items"]
    assert nested.source_array == "items"
    assert nested.array_operations is not None
    assert "Items" in nested.array_operations


def test_memory_cache_usage():
    """Test that memory caching is used for get_mapping."""
    mapping = MappingConfig(
        table_name="Cache Test",
        description="Testing memory cache",
        version="1.0",
        mappings=Mappings(
            direct_mappings={"id": "CoLD_ID"},
        ),
    )

    repo = MappingRepository(mappings_dict={"Cache Test": mapping})

    # First call
    mapping1 = repo.get_mapping("Cache Test")
    # Second call should return same object from cache dict
    mapping2 = repo.get_mapping("Cache Test")

    # Should return the same object (from cache dict)
    assert mapping1 is mapping2
    assert isinstance(mapping1, MappingConfig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
