import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from .models import ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def classify_themes(
    text: str,
    col_section: str,
    legal_system: str,
    jurisdiction: str | None,
):
    """
    Classify themes for a court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        model: Model to use for classification

    Returns:
        ThemeClassificationOutput: Classified themes with confidence and reasoning
    """
    with logfire.span("themes"):
        PIL_THEME_PROMPT = get_prompt_module(legal_system, "theme", jurisdiction).PIL_THEME_PROMPT

        prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "theme")

        try:
            agent = Agent(
                name="ThemeClassifier",
                instructions=system_prompt,
                output_type=ThemeClassificationOutput,
                model=OpenAIChatCompletionsModel(
                    model=get_model("themes"),
                    openai_client=get_openai_client(),
                ),
            )
            run_result = await Runner.run(agent, prompt)
            result = run_result.final_output_as(ThemeClassificationOutput)
            return result
        except Exception as e:
            logger.error("Error during theme classification: %s", e)
            fallback_reason = f"Classification failed: {str(e)}"
            return ThemeClassificationOutput(themes=["NA"], confidence="low", reasoning=fallback_reason)
