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
