"""Internal prompts module for case analyzer."""

from .legal_system_type_detection import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT
from .precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT
from .prompt_selector import get_prompt_module

__all__ = [
    "get_prompt_module",
    "LEGAL_SYSTEM_TYPE_DETECTION_PROMPT",
    "PRECISE_JURISDICTION_DETECTION_PROMPT",
]
