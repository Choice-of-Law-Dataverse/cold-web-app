import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from .models import StepResult, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def classify_themes(
    text: str,
    col_section: str,
    legal_system: str,
    jurisdiction: str | None,
    previous_response_id: str | None = None,
) -> StepResult[ThemeClassificationOutput]:
    with logfire.span("themes"):
        PIL_THEME_PROMPT = get_prompt_module(legal_system, "theme", jurisdiction).PIL_THEME_PROMPT

        prompt = PIL_THEME_PROMPT.format(text=text, col_section=col_section, themes_table=THEMES_TABLE_STR)
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "theme")

        try:
            agent = Agent(
                name="ThemeClassifier",
                instructions=system_prompt,
                output_type=ThemeClassificationOutput,
                model=OpenAIResponsesModel(
                    model=get_model("themes"),
                    openai_client=get_openai_client(),
                ),
            )
            run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
            result = run_result.final_output_as(ThemeClassificationOutput)
            return StepResult(output=result, response_id=run_result.last_response_id)
        except Exception as e:
            logger.error("Error during theme classification: %s", e)
            fallback_reason = f"Classification failed: {str(e)}"
            return StepResult(output=ThemeClassificationOutput(themes=["NA"], confidence="low", reasoning=fallback_reason))
