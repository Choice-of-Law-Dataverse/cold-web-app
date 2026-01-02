"""Tests for MappingRepository with Pydantic validation."""

import json
import tempfile
from pathlib import Path

import pytest

from app.schemas.mapping_schema import MappingConfig
from app.services.mapping_repository import MappingRepository


@pytest.fixture
def temp_mappings_dir():
    """Create a temporary directory with test mapping files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid mapping file
        valid_mapping = {
            "table_name": "TestTable",  # No spaces to avoid filename mismatch issues
            "description": "Test mapping",
            "version": "1.0",
            "mappings": {
                "direct_mappings": {
                    "id": "CoLD_ID",
                    "name": "Name",
                },
                "conditional_mappings": {
                    "sort_date": {
                        "primary": "updated_at",
                        "fallback": "created_at",
                    },
                },
            },
        }

        valid_file = Path(tmpdir) / "testtable_mapping.json"
        with open(valid_file, "w") as f:
            json.dump(valid_mapping, f)

        # Create an invalid mapping file (missing required fields)
        invalid_mapping = {
            "table_name": "InvalidTable",
            "description": "Missing version",
            # missing version and mappings
        }

        invalid_file = Path(tmpdir) / "invalidtable_mapping.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_mapping, f)

        yield tmpdir


def test_mapping_repository_loads_valid_mappings(temp_mappings_dir):
    """Test that MappingRepository loads and validates correct mappings."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    # Should have loaded the valid mapping
    mapping = repo.get_mapping("TestTable")
    assert mapping is not None
    assert isinstance(mapping, MappingConfig)
    assert mapping.table_name == "TestTable"
    assert mapping.version == "1.0"


def test_mapping_repository_handles_invalid_mappings(temp_mappings_dir):
    """Test that MappingRepository handles invalid mappings gracefully."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    # Invalid mapping should not be loaded (validation is required)
    mapping = repo.get_mapping("InvalidTable")
    # Invalid mappings are now skipped during load
    assert mapping is None


def test_mapping_repository_get_all_mappings(temp_mappings_dir):
    """Test getting all mappings."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    all_mappings = repo.get_all_mappings()
    assert len(all_mappings) >= 1  # At least the valid one
    assert "TestTable" in all_mappings


def test_mapping_repository_has_mapping(temp_mappings_dir):
    """Test checking if mapping exists."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    assert repo.has_mapping("TestTable") is True
    assert repo.has_mapping("Nonexistent Table") is False


def test_mapping_repository_get_supported_tables(temp_mappings_dir):
    """Test getting list of supported tables."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    tables = repo.get_supported_tables()
    assert "TestTable" in tables


def test_mapping_repository_reload_mapping(temp_mappings_dir):
    """Test reloading a specific mapping."""
    repo = MappingRepository(mappings_directory=temp_mappings_dir)

    # Reload the valid mapping
    result = repo.reload_mapping("TestTable")
    assert result is True

    # Try to reload nonexistent mapping
    result = repo.reload_mapping("Nonexistent Table")
    assert result is False


def test_mapping_repository_with_real_mappings():
    """Test MappingRepository with actual mapping files if they exist."""
    # Use default directory
    repo = MappingRepository()

    # If any mappings exist, they should be loaded
    tables = repo.get_supported_tables()
    if len(tables) > 0:
        # Pick first table and verify it's a MappingConfig
        first_table = tables[0]
        mapping = repo.get_mapping(first_table)
        assert mapping is not None
        # In validation mode, should be MappingConfig if valid
        if isinstance(mapping, MappingConfig):
            assert mapping.table_name == first_table


def test_mapping_config_type_safety():
    """Test that validated mappings provide type safety."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mapping_data = {
            "table_name": "Type Safety Test",
            "description": "Testing type safety",
            "version": "1.0",
            "mappings": {
                "direct_mappings": {
                    "id": "CoLD_ID",
                },
                "nested_mappings": {
                    "related_items": {
                        "source_array": "items",
                        "array_operations": {
                            "Items": {
                                "operation": "join",
                                "field": "name",
                                "separator": ", ",
                            },
                        },
                    },
                },
            },
        }

        mapping_file = Path(tmpdir) / "type_safety_test_mapping.json"
        with open(mapping_file, "w") as f:
            json.dump(mapping_data, f)

        repo = MappingRepository(mappings_directory=tmpdir)
        mapping = repo.get_mapping("Type Safety Test")

        assert isinstance(mapping, MappingConfig)
        # Type checkers can now infer these fields
        assert mapping.table_name == "Type Safety Test"
        assert "related_items" in mapping.mappings.nested_mappings
        nested = mapping.mappings.nested_mappings["related_items"]
        assert nested.source_array == "items"
        assert nested.array_operations is not None
        assert "Items" in nested.array_operations


def test_memory_cache_usage():
    """Test that memory caching is used for get_mapping."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mapping_data = {
            "table_name": "Cache Test",
            "description": "Testing memory cache",
            "version": "1.0",
            "mappings": {
                "direct_mappings": {"id": "CoLD_ID"},
            },
        }

        mapping_file = Path(tmpdir) / "cache_test_mapping.json"
        with open(mapping_file, "w") as f:
            json.dump(mapping_data, f)

        repo = MappingRepository(mappings_directory=tmpdir)

        # First call
        mapping1 = repo.get_mapping("Cache Test")
        # Second call should return same object from cache dict
        mapping2 = repo.get_mapping("Cache Test")

        # Should return the same object (from cache dict)
        assert mapping1 is mapping2
        assert isinstance(mapping1, MappingConfig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
