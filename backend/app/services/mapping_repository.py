"""
Mapping repository for managing transformation rules and configurations.
This module provides a centralized way to load and manage transformation
mappings from external configuration files with Pydantic validation.
"""

import json
import logging
import os

from pydantic import ValidationError

from app.schemas.mapping_schema import MappingConfig

logger = logging.getLogger(__name__)


class MappingRepository:
    """
    Repository class for managing transformation mapping configurations.
    Uses Pydantic for validation to ensure mapping files are correctly structured.
    All mappings are validated on load - validation is standard.
    Mappings are cached in memory for performance.
    """

    def __init__(self, mappings_directory: str | None = None):
        """
        Initialize the mapping repository.

        Args:
            mappings_directory (str): Path to the directory containing mapping files
        """
        if mappings_directory is None:
            # Default to the transformations directory relative to this file
            current_dir = os.path.dirname(__file__)
            self.mappings_directory = os.path.join(current_dir, "..", "mapping", "transformations")
        else:
            self.mappings_directory = mappings_directory

        self._cache: dict[str, MappingConfig] = {}
        self._load_all_mappings()

    def _load_all_mappings(self):
        """Load all mapping files from the mappings directory with validation."""
        try:
            if not os.path.exists(self.mappings_directory):
                logger.warning(f"Mappings directory not found: {self.mappings_directory}")
                return

            for filename in os.listdir(self.mappings_directory):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.mappings_directory, filename)
                    try:
                        with open(filepath, encoding="utf-8") as f:
                            mapping_data = json.load(f)

                            # Always validate with Pydantic
                            try:
                                mapping_config = MappingConfig(**mapping_data)
                                table_name = mapping_config.table_name
                                self._cache[table_name] = mapping_config
                                logger.info(f"Loaded and validated mapping for table: {table_name}")
                            except ValidationError as e:
                                logger.error(f"Validation error in mapping file {filename}: {e}")
                                # Validation is required - don't load invalid mappings
                                continue
                    except Exception as e:
                        logger.error(f"Error loading mapping file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error loading mappings directory: {e}")

    def get_mapping(self, table_name: str) -> MappingConfig | None:
        """
        Get the mapping configuration for a specific table.

        Mappings are cached in memory in the _cache dict for performance.

        Args:
            table_name (str): Name of the table

        Returns:
            MappingConfig | None: Validated mapping configuration or None if not found
        """
        return self._cache.get(table_name)

    def get_all_mappings(self) -> dict[str, MappingConfig]:
        """
        Get all loaded mapping configurations.

        Returns:
            dict: Dictionary of all mapping configurations keyed by table name
        """
        return self._cache.copy()

    def reload_mapping(self, table_name: str) -> bool:
        """
        Reload a specific mapping configuration from file.

        Args:
            table_name (str): Name of the table to reload

        Returns:
            bool: True if successfully reloaded, False otherwise
        """
        try:
            # Convert table name to filename: lowercase, replace spaces with underscores
            filename = f"{table_name.lower().replace(' ', '_')}_mapping.json"
            filepath = os.path.join(self.mappings_directory, filename)

            if os.path.exists(filepath):
                with open(filepath, encoding="utf-8") as f:
                    mapping_data = json.load(f)

                    # Always validate with Pydantic
                    try:
                        mapping_config = MappingConfig(**mapping_data)
                        self._cache[table_name] = mapping_config
                        logger.info(f"Reloaded and validated mapping for table: {table_name}")
                        return True
                    except ValidationError as e:
                        logger.error(f"Validation error reloading {table_name}: {e}")
                        return False
        except Exception as e:
            logger.error(f"Error reloading mapping for {table_name}: {e}")

        return False

    def has_mapping(self, table_name: str) -> bool:
        """
        Check if a mapping exists for the given table.

        Args:
            table_name (str): Name of the table

        Returns:
            bool: True if mapping exists, False otherwise
        """
        return table_name in self._cache

    def get_supported_tables(self) -> list[str]:
        """
        Get a list of all tables that have mapping configurations.

        Returns:
            list: List of table names
        """
        return list(self._cache.keys())


# Global instance for easy access
_mapping_repository = None


def get_mapping_repository() -> MappingRepository:
    """
    Get the global mapping repository instance (singleton pattern).

    Returns:
        MappingRepository: The global mapping repository instance with validation enabled
    """
    global _mapping_repository
    if _mapping_repository is None:
        _mapping_repository = MappingRepository()
    return _mapping_repository
