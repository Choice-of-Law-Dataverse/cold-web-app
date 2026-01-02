"""
Configuration-driven data transformer that uses external mapping rules.
This module provides a generic transformer that applies transformation rules
loaded from external configuration files via the mapping repository.
"""

import json
import logging
from typing import Any

from app.schemas.mapping_schema import MappingConfig, PostProcessing

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

    def transform(self, table_name: str, source_data: dict[str, Any]) -> dict[str, Any]:
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

    def _apply_mapping(self, source_data: dict[str, Any], mapping_config: MappingConfig) -> dict[str, Any]:
        """
        Apply the mapping configuration to transform the source data.

        Args:
            source_data (dict): The source data
            mapping_config (MappingConfig): The mapping configuration

        Returns:
            dict: Transformed data
        """
        transformed = {}
        mappings = mapping_config.mappings

        # Apply direct mappings
        self._apply_direct_mappings(source_data, transformed, mappings.direct_mappings)

        # Apply conditional mappings
        self._apply_conditional_mappings(source_data, transformed, mappings.conditional_mappings)

        # Apply nested mappings
        self._apply_nested_mappings(source_data, transformed, mappings.nested_mappings)

        # Apply complex mappings
        self._apply_complex_mappings(source_data, transformed, mappings.complex_mappings)

        # Apply user mappings
        self._apply_user_mappings(source_data, transformed, mappings.user_mappings)

        # Apply boolean mappings
        self._apply_boolean_mappings(source_data, transformed, mappings.boolean_mappings)

        # Apply post-processing
        self._apply_post_processing(transformed, mapping_config.post_processing)

        return transformed

    def _apply_direct_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        direct_mappings: dict[str, str],
    ):
        """Apply direct field mappings."""
        for target_field, source_field in direct_mappings.items():
            if source_field in source_data:
                transformed[target_field] = source_data[source_field]

    def _apply_conditional_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        conditional_mappings: dict[str, Any],
    ):
        """Apply conditional field mappings with fallbacks."""
        for target_field, condition_config in conditional_mappings.items():
            primary_field = condition_config.primary
            fallback_field = condition_config.fallback

            if primary_field and primary_field in source_data and source_data[primary_field] is not None:
                transformed[target_field] = source_data[primary_field]
            elif fallback_field and fallback_field in source_data:
                transformed[target_field] = source_data[fallback_field]

    def _apply_nested_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        nested_mappings: dict[str, Any],
    ):
        """Apply nested field mappings for related data."""
        for _mapping_name, mapping_config in nested_mappings.items():
            source_array_name = mapping_config.source_array
            if not source_array_name:
                continue

            # Support dotted paths, e.g., 'hop1_relations.related_items'
            def _resolve_path(data, path: str):
                cur = data
                for part in path.split("."):
                    if isinstance(cur, dict) and part in cur:
                        cur = cur[part]
                    else:
                        return None
                return cur

            source_array = (
                source_data.get(source_array_name)
                if source_array_name in source_data
                else _resolve_path(source_data, source_array_name)
            )
            if not isinstance(source_array, list) or not source_array:
                continue

            # Get the specified index (default to 0)
            index = mapping_config.index if mapping_config.index is not None else 0
            if index >= len(source_array):
                continue

            source_item = source_array[index]

            # Apply direct mappings for nested items
            direct_mappings = mapping_config.mappings or {}
            for target_field, source_field in direct_mappings.items():
                if source_field in source_item:
                    transformed[target_field] = source_item[source_field]

            # Apply conditional mappings for nested items
            conditional_mappings = mapping_config.conditional_mappings or {}
            self._apply_conditional_mappings(source_item, transformed, conditional_mappings)

            # Apply boolean mappings
            boolean_mappings = mapping_config.boolean_mappings or {}
            self._apply_boolean_mappings(source_item, transformed, boolean_mappings)

            # Apply array operations
            array_operations = mapping_config.array_operations or {}
            self._apply_array_operations(source_array, transformed, array_operations)

    def _apply_boolean_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        boolean_mappings: dict[str, Any],
    ):
        """Apply boolean field mappings."""
        for target_field, boolean_config in boolean_mappings.items():
            source_field = boolean_config.source_field
            true_value = boolean_config.true_value
            false_value = boolean_config.false_value

            if source_field in source_data:
                source_value = source_data[source_field]
                if source_value is True:
                    transformed[target_field] = true_value
                elif source_value is False:
                    transformed[target_field] = false_value
                else:
                    # Handle truthy/falsy values
                    transformed[target_field] = true_value if source_value else false_value

    def _apply_array_operations(
        self,
        source_array: list[dict[str, Any]],
        transformed: dict[str, Any],
        array_operations: dict[str, Any],
    ):
        """Apply operations on arrays of data."""
        for target_field, operation_config in array_operations.items():
            operation = operation_config.operation
            field = operation_config.field
            separator = operation_config.separator

            if operation == "join" and field:
                values = [item.get(field) for item in source_array if item.get(field)]
                if values:
                    transformed[target_field] = separator.join(str(v) for v in values)

    def _apply_complex_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        complex_mappings: dict[str, Any],
    ):
        """Apply complex field mappings like JSON extraction."""
        for target_field, mapping_config in complex_mappings.items():
            source_field = mapping_config.source_field
            mapping_type = mapping_config.type
            operation = mapping_config.operation

            if not source_field or source_field not in source_data:
                continue

            source_value = source_data[source_field]

            if mapping_type == "json_extract" and operation == "first_item_as_airtable_format":
                try:
                    # Parse JSON string and convert to Airtable-like format
                    if isinstance(source_value, str):
                        json_data = json.loads(source_value)
                        if isinstance(json_data, list) and json_data:
                            first_item = json_data[0]
                            # Convert to Airtable format
                            airtable_format = {
                                "id": first_item.get("id", ""),
                                "url": first_item.get("url", ""),
                                "filename": first_item.get("title", ""),
                                "size": first_item.get("size", 0),
                                "type": first_item.get("mimetype", ""),
                                # Add thumbnails if needed
                            }
                            transformed[target_field] = str(airtable_format)
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logger.warning(f"Error processing complex mapping for {target_field}: {e}")
            elif mapping_type == "array_extract" and operation == "first_item":
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

            elif mapping_type == "array_extract":
                try:
                    # Handle different array extraction operations
                    if isinstance(source_value, list):
                        if operation == "join_ids":
                            # Extract numeric IDs and join with commas
                            ids = [str(item.get("id", "")) for item in source_value if item.get("id")]
                            transformed[target_field] = ",".join(ids)
                        elif operation == "join_record_ids":
                            # Extract record IDs and join with commas
                            record_ids = [item.get("ncRecordId", "") for item in source_value if item.get("ncRecordId")]
                            transformed[target_field] = ",".join(record_ids)
                        elif operation == "join_display_values":
                            # Extract display_value field from each item and join
                            display_values = [
                                item.get("display_value", "") for item in source_value if item.get("display_value")
                            ]
                            transformed[target_field] = ",".join(display_values)
                    elif isinstance(source_value, str):
                        # If it's already a string, assume it's properly formatted
                        transformed[target_field] = source_value
                except (KeyError, AttributeError) as e:
                    logger.warning(f"Error processing array extraction for {target_field}: {e}")
                    transformed[target_field] = source_value

    def _apply_user_mappings(
        self,
        source_data: dict[str, Any],
        transformed: dict[str, Any],
        user_mappings: dict[str, Any],
    ):
        """Apply user field mappings for extracting user information."""
        for _mapping_name, mapping_config in user_mappings.items():
            source_field = mapping_config.source_field
            user_fields = mapping_config.user_fields

            if not source_field or source_field not in source_data:
                continue

            user_data = source_data[source_field]

            # Handle both dict user objects and simple string IDs
            if isinstance(user_data, dict):
                # User data is already a dict with id, email, name
                for target_field, user_attribute in user_fields.items():
                    if user_attribute in user_data:
                        transformed[target_field] = user_data[user_attribute]
            else:
                # User data is just an ID string - generate placeholder values
                user_id = user_data
                for target_field, user_attribute in user_fields.items():
                    if user_attribute == "id":
                        transformed[target_field] = user_id
                    elif user_attribute == "email":
                        transformed[target_field] = f"user{user_id}@example.com"
                    elif user_attribute == "name":
                        transformed[target_field] = f"User {user_id}"

    def _apply_post_processing(self, transformed: dict[str, Any], post_processing: PostProcessing):
        """Apply post-processing rules to the transformed data."""
        if post_processing.remove_null_values:
            # Remove keys with None values in-place
            keys_to_remove = [k for k, v in transformed.items() if v is None]
            for k in keys_to_remove:
                del transformed[k]

        # Note: remove_empty_strings is not in the PostProcessing model
        # If needed, this should be added to the schema

        return transformed

    def get_reverse_field_mapping(self, table_name: str) -> dict[str, str]:
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
        mappings = mapping_config.mappings

        # Reverse direct mappings
        for target_field, source_field in mappings.direct_mappings.items():
            reverse_mapping[target_field] = source_field

        # Reverse conditional mappings (use primary field)
        for target_field, condition_config in mappings.conditional_mappings.items():
            primary_field = condition_config.primary
            if primary_field:
                reverse_mapping[target_field] = primary_field

        # Reverse boolean mappings
        for target_field, boolean_config in mappings.boolean_mappings.items():
            reverse_mapping[target_field] = boolean_config.source_field

        # Handle nested mappings (from related data)
        nested_mappings = mappings.nested_mappings
        for _mapping_name, mapping_config in nested_mappings.items():
            direct_mappings = mapping_config.mappings or {}
            for target_field, source_field in direct_mappings.items():
                # For nested mappings, we can't directly reverse map since they come from arrays
                # But we can at least note the relationship
                reverse_mapping[target_field] = f"{mapping_config.source_array}.{source_field}"

            # Include array_operations (e.g., joins) to allow filtering by user-faced aggregated names
            array_ops = mapping_config.array_operations or {}
            for target_field, op_cfg in array_ops.items():
                # Map to underlying array field path for reverse lookup
                field = op_cfg.field
                if field:
                    reverse_mapping[target_field] = f"{mapping_config.source_array}.{field}"

            # Include nested boolean_mappings
            boolean_mappings_nested = mapping_config.boolean_mappings or {}
            for target_field, boolean_config in boolean_mappings_nested.items():
                src = boolean_config.source_field
                if src:
                    reverse_mapping[target_field] = f"{mapping_config.source_array}.{src}"

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
