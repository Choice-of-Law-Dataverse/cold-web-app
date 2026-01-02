"""
Mapping repository for managing transformation rules and configurations.
This module provides a centralized way to load and manage transformation
mappings from Python class-based configurations.
"""

import logging

from app.schemas.mapping_schema import MappingConfig

logger = logging.getLogger(__name__)


class MappingRepository:
    """
    Repository class for managing transformation mapping configurations.
    Loads mappings from Python class-based configurations for better type safety
    and maintainability. All mappings are validated at import time by Pydantic.
    Mappings are cached in memory for performance.
    """

    def __init__(self, mappings_dict: dict[str, MappingConfig] | None = None):
        """
        Initialize the mapping repository.

        Args:
            mappings_dict: Optional dictionary of mappings. If None, loads from default configs.
        """
        self._cache: dict[str, MappingConfig] = {}
        self._load_all_mappings(mappings_dict)

    def _load_all_mappings(self, mappings_dict: dict[str, MappingConfig] | None = None):
        """Load all mapping configurations from Python classes."""
        try:
            if mappings_dict is None:
                # Import the default mappings from configs module
                from app.mapping.configs import ALL_MAPPINGS

                mappings_dict = ALL_MAPPINGS

            for table_name, mapping_config in mappings_dict.items():
                self._cache[table_name] = mapping_config
                logger.info(f"Loaded mapping for table: {table_name}")

        except Exception as e:
            logger.error(f"Error loading mappings: {e}")

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
