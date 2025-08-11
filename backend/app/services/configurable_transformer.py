"""
Configuration-driven data transformer that uses external mapping rules.
This module provides a generic transformer that applies transformation rules
loaded from external configuration files via the mapping repository.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from .mapping_repository import get_mapping_repository

logger = logging.getLogger(__name__)


class ConfigurableTransformer:
    """
    A configurable transformer that applies transformation rules from external configuration.
    """
    
    def __init__(self, mapping_repository=None):
        """
        Initialize the configurable transformer.
        
        Args:
            mapping_repository: Optional mapping repository instance
        """
        self.mapping_repo = mapping_repository or get_mapping_repository()
    
    def transform(self, table_name: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform source data using the mapping configuration for the given table.
        
        Args:
            table_name (str): Name of the source table
            source_data (dict): The source data to transform
            
        Returns:
            dict: Transformed data
        """
        mapping_config = self.mapping_repo.get_mapping(table_name)
        if not mapping_config:
            logger.debug(f"No mapping configuration found for table: {table_name}")
            return source_data
        
        try:
            return self._apply_mapping(source_data, mapping_config)
        except Exception as e:
            logger.error(f"Error applying transformation for {table_name}: {e}")
            return source_data
    
    def _apply_mapping(self, source_data: Dict[str, Any], mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the mapping configuration to transform the source data.
        
        Args:
            source_data (dict): The source data
            mapping_config (dict): The mapping configuration
            
        Returns:
            dict: Transformed data
        """
        transformed = {}
        mappings = mapping_config.get('mappings', {})
        
        # Apply direct mappings
        self._apply_direct_mappings(source_data, transformed, mappings.get('direct_mappings', {}))
        
        # Apply conditional mappings
        self._apply_conditional_mappings(source_data, transformed, mappings.get('conditional_mappings', {}))
        
        # Apply nested mappings
        self._apply_nested_mappings(source_data, transformed, mappings.get('nested_mappings', {}))
        
        # Apply complex mappings
        self._apply_complex_mappings(source_data, transformed, mappings.get('complex_mappings', {}))
        
        # Apply user mappings
        self._apply_user_mappings(source_data, transformed, mappings.get('user_mappings', {}))
        
        # Apply boolean mappings
        self._apply_boolean_mappings(source_data, transformed, mappings.get('boolean_mappings', {}))
        
        # Apply post-processing
        self._apply_post_processing(transformed, mapping_config.get('post_processing', {}))
        
        return transformed
    
    def _apply_direct_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], direct_mappings: Dict[str, str]):
        """Apply direct field mappings."""
        for target_field, source_field in direct_mappings.items():
            if source_field in source_data:
                transformed[target_field] = source_data[source_field]
    
    def _apply_conditional_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], conditional_mappings: Dict[str, Dict[str, str]]):
        """Apply conditional field mappings with fallbacks."""
        for target_field, condition_config in conditional_mappings.items():
            primary_field = condition_config.get('primary')
            fallback_field = condition_config.get('fallback')
            
            if primary_field and primary_field in source_data and source_data[primary_field] is not None:
                transformed[target_field] = source_data[primary_field]
            elif fallback_field and fallback_field in source_data:
                transformed[target_field] = source_data[fallback_field]
    
    def _apply_nested_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], nested_mappings: Dict[str, Dict[str, Any]]):
        """Apply nested field mappings for related data."""
        for mapping_name, mapping_config in nested_mappings.items():
            source_array_name = mapping_config.get('source_array')
            if not source_array_name or source_array_name not in source_data:
                continue
            
            source_array = source_data[source_array_name]
            if not isinstance(source_array, list) or not source_array:
                continue
            
            # Get the specified index (default to 0)
            index = mapping_config.get('index', 0)
            if index >= len(source_array):
                continue
            
            source_item = source_array[index]
            
            # Apply direct mappings for nested items
            direct_mappings = mapping_config.get('mappings', {})
            for target_field, source_field in direct_mappings.items():
                if source_field in source_item:
                    transformed[target_field] = source_item[source_field]
            
            # Apply conditional mappings for nested items
            conditional_mappings = mapping_config.get('conditional_mappings', {})
            self._apply_conditional_mappings(source_item, transformed, conditional_mappings)
            
            # Apply boolean mappings
            boolean_mappings = mapping_config.get('boolean_mappings', {})
            self._apply_boolean_mappings(source_item, transformed, boolean_mappings)
            
            # Apply array operations
            array_operations = mapping_config.get('array_operations', {})
            self._apply_array_operations(source_array, transformed, array_operations)
    
    def _apply_boolean_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], boolean_mappings: Dict[str, Dict[str, str]]):
        """Apply boolean field mappings."""
        for target_field, boolean_config in boolean_mappings.items():
            source_field = boolean_config.get('source_field')
            true_value = boolean_config.get('true_value')
            false_value = boolean_config.get('false_value')
            
            if source_field in source_data:
                source_value = source_data[source_field]
                if source_value is True:
                    transformed[target_field] = true_value
                elif source_value is False:
                    transformed[target_field] = false_value
                else:
                    # Handle truthy/falsy values
                    transformed[target_field] = true_value if source_value else false_value
    
    def _apply_array_operations(self, source_array: List[Dict[str, Any]], transformed: Dict[str, Any], array_operations: Dict[str, Dict[str, str]]):
        """Apply operations on arrays of data."""
        for target_field, operation_config in array_operations.items():
            operation = operation_config.get('operation')
            field = operation_config.get('field')
            
            if operation == 'join' and field:
                separator = operation_config.get('separator', ', ')
                values = [item.get(field) for item in source_array if item.get(field)]
                if values:
                    transformed[target_field] = separator.join(str(v) for v in values)
    
    def _apply_complex_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], complex_mappings: Dict[str, Dict[str, str]]):
        """Apply complex field mappings like JSON extraction."""
        for target_field, mapping_config in complex_mappings.items():
            source_field = mapping_config.get('source_field')
            mapping_type = mapping_config.get('type')
            operation = mapping_config.get('operation')
            
            if not source_field or source_field not in source_data:
                continue
            
            source_value = source_data[source_field]
            
            if mapping_type == 'json_extract' and operation == 'first_item_as_airtable_format':
                try:
                    # Parse JSON string and convert to Airtable-like format
                    if isinstance(source_value, str):
                        json_data = json.loads(source_value)
                        if isinstance(json_data, list) and json_data:
                            first_item = json_data[0]
                            # Convert to Airtable format
                            airtable_format = {
                                'id': first_item.get('id', ''),
                                'url': first_item.get('url', ''),
                                'filename': first_item.get('title', ''),
                                'size': first_item.get('size', 0),
                                'type': first_item.get('mimetype', ''),
                                # Add thumbnails if needed
                            }
                            transformed[target_field] = str(airtable_format)
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logger.warning(f"Error processing complex mapping for {target_field}: {e}")
            elif mapping_type == 'array_extract' and operation == 'first_item':
                try:
                    # Extract first item from array
                    if isinstance(source_value, list) and source_value:
                        transformed[target_field] = source_value[0]
                    elif source_value is not None:
                        # If it's not an array, use the value as is
                        transformed[target_field] = source_value
                except (KeyError, IndexError) as e:
                    logger.warning(f"Error processing array_extract mapping for {target_field}: {e}")
                    transformed[target_field] = source_value
            
            elif mapping_type == 'array_extract':
                try:
                    # Handle different array extraction operations
                    if isinstance(source_value, list):
                        if operation == 'join_ids':
                            # Extract numeric IDs and join with commas
                            ids = [str(item.get('id', '')) for item in source_value if item.get('id')]
                            transformed[target_field] = ','.join(ids)
                        elif operation == 'join_record_ids':
                            # Extract record IDs and join with commas
                            record_ids = [item.get('ncRecordId', '') for item in source_value if item.get('ncRecordId')]
                            transformed[target_field] = ','.join(record_ids)
                        elif operation == 'join_display_values':
                            # Create display values in the format "ID Field_Value"
                            display_values = []
                            for item in source_value:
                                item_id = item.get('id', '')
                                # This would typically be a more complex lookup in a real system
                                display_values.append(f"{target_field.split()[0]}-{item_id}")
                            transformed[target_field] = ','.join(display_values)
                    elif isinstance(source_value, str):
                        # If it's already a string, assume it's properly formatted
                        transformed[target_field] = source_value
                except (KeyError, AttributeError) as e:
                    logger.warning(f"Error processing array extraction for {target_field}: {e}")
                    transformed[target_field] = source_value
    
    def _apply_user_mappings(self, source_data: Dict[str, Any], transformed: Dict[str, Any], user_mappings: Dict[str, Dict[str, Any]]):
        """Apply user field mappings for extracting user information."""
        for mapping_name, mapping_config in user_mappings.items():
            source_field = mapping_config.get('source_field')
            user_fields = mapping_config.get('user_fields', {})
            
            if not source_field or source_field not in source_data:
                continue
            
            user_id = source_data[source_field]
            
            # For now, we'll just map the user ID to the specified fields
            # In a real implementation, you might want to look up user details from a user service
            for target_field, user_attribute in user_fields.items():
                if user_attribute == 'id':
                    transformed[target_field] = user_id
                elif user_attribute == 'email':
                    # Placeholder - in real implementation, look up email from user service
                    transformed[target_field] = f"user{user_id}@example.com"
                elif user_attribute == 'name':
                    # Placeholder - in real implementation, look up name from user service
                    transformed[target_field] = f"User {user_id}"
    
    def _apply_post_processing(self, transformed: Dict[str, Any], post_processing: Dict[str, Any]):
        """Apply post-processing rules to the transformed data."""
        if post_processing.get('remove_null_values', False):
            transformed = {k: v for k, v in transformed.items() if v is not None}
        
        if post_processing.get('remove_empty_strings', False):
            transformed = {k: v for k, v in transformed.items() if v != ''}
        
        return transformed
    
    def get_reverse_field_mapping(self, table_name: str) -> Dict[str, str]:
        """
        Create a reverse mapping from transformed field names back to source field names.
        This is useful for filtering operations that need to work on raw data.
        
        Args:
            table_name (str): Name of the source table
            
        Returns:
            dict: Mapping from transformed field names to source field names
        """
        mapping_config = self.mapping_repo.get_mapping(table_name)
        if not mapping_config:
            return {}
        
        reverse_mapping = {}
        mappings = mapping_config.get('mappings', {})
        
        # Reverse direct mappings
        direct_mappings = mappings.get('direct_mappings', {})
        for target_field, source_field in direct_mappings.items():
            reverse_mapping[target_field] = source_field
        
        # Reverse conditional mappings (use primary field)
        conditional_mappings = mappings.get('conditional_mappings', {})
        for target_field, condition_config in conditional_mappings.items():
            primary_field = condition_config.get('primary')
            if primary_field:
                reverse_mapping[target_field] = primary_field
        
        # Reverse boolean mappings
        boolean_mappings = mappings.get('boolean_mappings', {})
        for target_field, boolean_config in boolean_mappings.items():
            source_field = boolean_config.get('source_field')
            if source_field:
                reverse_mapping[target_field] = source_field
        
        # Handle nested mappings (from related data)
        nested_mappings = mappings.get('nested_mappings', {})
        for mapping_name, mapping_config in nested_mappings.items():
            direct_mappings = mapping_config.get('mappings', {})
            for target_field, source_field in direct_mappings.items():
                # For nested mappings, we can't directly reverse map since they come from arrays
                # But we can at least note the relationship
                reverse_mapping[target_field] = f"{mapping_config.get('source_array')}.{source_field}"
        
        return reverse_mapping


# Global instance for easy access
_configurable_transformer = None

def get_configurable_transformer() -> ConfigurableTransformer:
    """
    Get the global configurable transformer instance (singleton pattern).
    
    Returns:
        ConfigurableTransformer: The global configurable transformer instance
    """
    global _configurable_transformer
    if _configurable_transformer is None:
        _configurable_transformer = ConfigurableTransformer()
    return _configurable_transformer
