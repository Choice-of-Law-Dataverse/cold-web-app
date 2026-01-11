"""Internal prompts module for case analyzer.

This module provides a centralized prompt management system with:
- Registry-based prompt storage and retrieval
- Prompt metadata and versioning
- Backward-compatible API for existing code
- Easy discovery and listing of available prompts
"""

from .base import BasePrompt, PromptMetadata, get_registry
from .legal_system_type_detection import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT
from .precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT
from .prompt_selector import get_prompt_module
from .prompt_selector_v2 import (
    get_prompt_from_registry,
    get_prompt_info,
    list_available_prompts,
)

__all__ = [
    # Legacy API (backward compatible)
    "get_prompt_module",
    "LEGAL_SYSTEM_TYPE_DETECTION_PROMPT",
    "PRECISE_JURISDICTION_DETECTION_PROMPT",
    # New registry-based API
    "get_registry",
    "get_prompt_from_registry",
    "get_prompt_info",
    "list_available_prompts",
    # Base classes for custom prompts
    "BasePrompt",
    "PromptMetadata",
]
