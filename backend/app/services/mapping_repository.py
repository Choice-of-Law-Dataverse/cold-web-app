"""
Mapping repository for managing transformation rules and configurations.
This module provides a centralized way to load and manage transformation
mappings from external configuration files.
"""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MappingRepository:
    """
    Repository class for managing transformation mapping configurations.
    """
    
    def __init__(self, mappings_directory: str = None):
        """
        Initialize the mapping repository.
        
        Args:
            mappings_directory (str): Path to the directory containing mapping files
        """
        if mappings_directory is None:
            # Default to the transformations directory relative to this file
            current_dir = os.path.dirname(__file__)
            self.mappings_directory = os.path.join(
                current_dir, "..", "mapping", "transformations"
            )
        else:
            self.mappings_directory = mappings_directory
        
        self._cache = {}
        self._load_all_mappings()
    
    def _load_all_mappings(self):
        """Load all mapping files from the mappings directory."""
        try:
            if not os.path.exists(self.mappings_directory):
                logger.warning(f"Mappings directory not found: {self.mappings_directory}")
                return
            
            for filename in os.listdir(self.mappings_directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.mappings_directory, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            mapping_config = json.load(f)
                            table_name = mapping_config.get('table_name')
                            if table_name:
                                self._cache[table_name] = mapping_config
                                logger.info(f"Loaded mapping for table: {table_name}")
                    except Exception as e:
                        logger.error(f"Error loading mapping file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error loading mappings directory: {e}")
    
    def get_mapping(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the mapping configuration for a specific table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            dict: Mapping configuration or None if not found
        """
        return self._cache.get(table_name)
    
    def get_all_mappings(self) -> Dict[str, Dict[str, Any]]:
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
            filename = f"{table_name.lower()}_mapping.json"
            filepath = os.path.join(self.mappings_directory, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    mapping_config = json.load(f)
                    self._cache[table_name] = mapping_config
                    logger.info(f"Reloaded mapping for table: {table_name}")
                    return True
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
    
    def get_supported_tables(self) -> list:
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
        MappingRepository: The global mapping repository instance
    """
    global _mapping_repository
    if _mapping_repository is None:
        _mapping_repository = MappingRepository()
    return _mapping_repository
