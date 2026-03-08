import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import generate_system_prompt
from .models import ColSectionOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_col_section(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
    previous_response_id: str | None = None,
) -> StepResult[ColSectionOutput]:
    with logfire.span("col_section"):
        COL_SECTION_PROMPT = get_prompt_module(legal_system, "col_section", jurisdiction).COL_SECTION_PROMPT

        prompt = COL_SECTION_PROMPT.format(text=text)

        system_prompt = generate_system_prompt(legal_system, jurisdiction, "col_section")

        agent = Agent(
            name="ColSectionExtractor",
            instructions=system_prompt,
            output_type=ColSectionOutput,
            model=OpenAIResponsesModel(
                model=get_model("col_section"),
                openai_client=get_openai_client(),
            ),
        )

        try:
            run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
            result = run_result.final_output_as(ColSectionOutput)
            return StepResult(output=result, response_id=run_result.last_response_id)
        except Exception as e:
            logger.error("Error in extract_col_section: %s", e)
            raise
