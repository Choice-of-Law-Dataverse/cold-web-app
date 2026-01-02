"""
Enums for categorical mapping values.

This module defines enums for common categorical values used in mappings
to provide type safety and better IDE support.
"""

from enum import Enum


class YesNoValue(str, Enum):
    """Enum for Yes/No/None string values."""

    YES = "Yes"
    NO = "No"
    NONE = "None"


class TrueFalse(str, Enum):
    """Enum for true/false string values."""

    TRUE = "true"
    FALSE = "false"


class Separator(str, Enum):
    """Common separators for join operations."""

    COMMA = ","
    COMMA_SPACE = ", "
    SEMICOLON = ";"
    PIPE = "|"


class ComplexMappingType(str, Enum):
    """Types of complex field transformations."""

    ARRAY_EXTRACT = "array_extract"
    JSON_EXTRACT = "json_extract"


class ComplexOperationType(str, Enum):
    """Operation types for complex field transformations."""

    JOIN_RECORD_IDS = "join_record_ids"
    JOIN_DISPLAY_VALUES = "join_display_values"
    FIRST_ITEM_AS_AIRTABLE_FORMAT = "first_item_as_airtable_format"
    JOIN_IDS = "join_ids"
