"""Enhanced prompt selector using the prompt registry.

This module provides backward-compatible functions for getting prompts
while using the new registry system under the hood.
"""

import logging
from types import ModuleType

from .base import get_registry

logger = logging.getLogger(__name__)

# Map user-facing jurisdiction to internal keys
JURISDICTION_MAP = {
    "Civil-law jurisdiction": "civil-law",
    "Common-law jurisdiction": "common-law",
}


def get_prompt_from_registry(
    jurisdiction: str, prompt_type: str, specific_jurisdiction: str | None = None
) -> str | None:
    """
    Get a prompt template from the registry.

    Args:
        jurisdiction: The legal system type (e.g., 'Civil-law jurisdiction')
        prompt_type: The type of prompt needed (e.g., 'col_section', 'theme', 'facts')
        specific_jurisdiction: The specific jurisdiction name (e.g., 'India')

    Returns:
        The prompt template string or None if not found
    """
    registry = get_registry()

    # Map user-facing jurisdiction to internal key
    legal_system = JURISDICTION_MAP.get(jurisdiction)
    if not legal_system:
        logger.warning("Unknown jurisdiction: %s", jurisdiction)
        legal_system = "civil-law"  # Default fallback

    # Check for India-specific prompts
    jurisdiction_key = None
    if specific_jurisdiction and specific_jurisdiction.lower() == "india":
        jurisdiction_key = "india"

    # Get the prompt from registry
    prompt_obj = registry.get(
        legal_system=legal_system,
        jurisdiction=jurisdiction_key,
        prompt_type=prompt_type,
    )

    if prompt_obj:
        return prompt_obj.get_template()

    logger.warning(
        "Prompt not found: legal_system=%s, jurisdiction=%s, type=%s",
        legal_system,
        jurisdiction_key,
        prompt_type,
    )
    return None


class PromptModuleWrapper:
    """
    Wrapper to make prompts accessible as module attributes.

    This provides backward compatibility with the old module-based approach.
    """

    def __init__(
        self, legal_system: str, jurisdiction: str | None, prompt_category: str
    ):
        self.legal_system = legal_system
        self.jurisdiction = jurisdiction
        self.prompt_category = prompt_category
        self._registry = get_registry()

    def __getattr__(self, name: str) -> str:
        """Get a prompt attribute dynamically."""
        # Map attribute names to prompt types
        type_map = {
            "COL_SECTION_PROMPT": "col_section",
            "PIL_THEME_PROMPT": "theme",
            "FACTS_PROMPT": "facts",
            "PIL_PROVISIONS_PROMPT": "pil_provisions",
            "COL_ISSUE_PROMPT": "col_issue",
            "COURTS_POSITION_PROMPT": "courts_position",
            "COURTS_POSITION_OBITER_DICTA_PROMPT": "obiter_dicta",
            "COURTS_POSITION_DISSENTING_OPINIONS_PROMPT": "dissenting_opinions",
            "ABSTRACT_PROMPT": "abstract",
        }

        if name in type_map:
            prompt_type = type_map[name]
            prompt_obj = self._registry.get(
                legal_system=self.legal_system,
                jurisdiction=self.jurisdiction,
                prompt_type=prompt_type,
            )

            if prompt_obj:
                return prompt_obj.get_template()

            raise AttributeError(
                f"Prompt '{name}' not found for legal_system={self.legal_system}, "
                f"jurisdiction={self.jurisdiction}, type={prompt_type}"
            )

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )


def get_prompt_module(
    jurisdiction: str, prompt_type: str, specific_jurisdiction: str | None = None
) -> ModuleType | PromptModuleWrapper:
    """
    Get the appropriate prompt module based on jurisdiction and specific jurisdiction.

    This function maintains backward compatibility with the old system while using
    the new registry under the hood.

    Args:
        jurisdiction: The legal system type (e.g., 'Civil-law jurisdiction', 'Common-law jurisdiction')
        prompt_type: The type of prompt needed ('col_section', 'theme', 'analysis')
        specific_jurisdiction: The specific jurisdiction name (e.g., 'India')

    Returns:
        A module wrapper that provides access to prompts via attributes
    """
    # Map user-facing jurisdiction to internal key
    legal_system = JURISDICTION_MAP.get(jurisdiction, "civil-law")

    # Check for India-specific prompts
    jurisdiction_key = None
    if specific_jurisdiction and specific_jurisdiction.lower() == "india":
        jurisdiction_key = "india"

    # For 'analysis' type, we need to return a wrapper that can provide multiple prompts
    # For other types, we can return a wrapper that maps to the specific prompt type
    return PromptModuleWrapper(legal_system, jurisdiction_key, prompt_type)


def list_available_prompts() -> list[dict]:
    """
    List all available prompts in the registry.

    Returns:
        List of prompt information dictionaries
    """
    registry = get_registry()
    return [prompt.get_info() for prompt in registry.list_all()]


def get_prompt_info(
    legal_system: str, jurisdiction: str | None, prompt_type: str
) -> dict | None:
    """
    Get information about a specific prompt.

    Args:
        legal_system: The legal system (e.g., 'civil-law', 'common-law')
        jurisdiction: The specific jurisdiction (e.g., 'india')
        prompt_type: The prompt type (e.g., 'col_section', 'abstract')

    Returns:
        Prompt information dictionary or None if not found
    """
    registry = get_registry()
    prompt_obj = registry.get(
        legal_system=legal_system, jurisdiction=jurisdiction, prompt_type=prompt_type
    )

    if prompt_obj:
        return prompt_obj.get_info()

    return None
