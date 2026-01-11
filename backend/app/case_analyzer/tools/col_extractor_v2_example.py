"""Example: Alternative implementation using the new registry API.

This file shows how tools can optionally use the new registry-based API
for improved type safety, validation, and discoverability.

The original implementation in col_extractor.py uses the backward-compatible API.
This file demonstrates the new approach for comparison.
"""

import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from ..config import get_model, get_openai_client
from ..prompts import get_registry
from ..utils import generate_system_prompt
from .models import ColSectionOutput

logger = logging.getLogger(__name__)


async def extract_col_section_v2(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
):
    """
    Extract Choice of Law section from court decision text.

    This version uses the new registry-based API for prompt management.

    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")

    Returns:
        ColSectionOutput: Extracted sections with confidence and reasoning
    """
    with logfire.span("col_section"):
        # Get the registry
        registry = get_registry()

        # Map user-facing jurisdiction to internal key
        legal_system_key = {
            "Civil-law jurisdiction": "civil-law",
            "Common-law jurisdiction": "common-law",
        }.get(legal_system, "civil-law")

        # Check for India-specific prompts
        jurisdiction_key = None
        if jurisdiction and jurisdiction.lower() == "india":
            jurisdiction_key = "india"

        # Get the prompt object from registry
        prompt_obj = registry.get(
            legal_system=legal_system_key,
            jurisdiction=jurisdiction_key,
            prompt_type="col_section",
        )

        if not prompt_obj:
            raise ValueError(
                f"No prompt found for legal_system={legal_system_key}, "
                f"jurisdiction={jurisdiction_key}, type=col_section"
            )

        # Get prompt info for logging
        info = prompt_obj.get_info()
        logger.info(
            "Using prompt: %s (v%s) - %s",
            info["name"],
            info["version"],
            info["description"],
        )

        # Format the prompt with automatic validation
        try:
            prompt = prompt_obj.format(text=text)
        except ValueError as e:
            logger.error("Failed to format prompt: %s", e)
            raise

        # Generate system prompt
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "col_section")

        # Create and run the agent
        agent = Agent(
            name="ColSectionExtractor",
            instructions=system_prompt,
            output_type=ColSectionOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("col_section"),
                openai_client=get_openai_client(),
            ),
        )

        try:
            run_result = await Runner.run(agent, prompt)
            result = run_result.final_output_as(ColSectionOutput)
            return result
        except Exception as e:
            logger.error("Error in extract_col_section_v2: %s", e)
            raise


# Benefits of the new approach:
# 1. Automatic parameter validation (missing parameters caught early)
# 2. Type-safe access to prompts via registry
# 3. Logging of prompt metadata (version, description)
# 4. Clear error messages when prompts are not found
# 5. Easy to discover available prompts for a legal system
# 6. Testable without actual LLM calls (can test prompt selection logic)
