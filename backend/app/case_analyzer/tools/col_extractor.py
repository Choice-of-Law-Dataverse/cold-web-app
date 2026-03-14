import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_col_section
from ..prompts import get_prompt_module
from ..runner import run_with_retry
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
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

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
            return await run_with_retry(
                agent,
                prompt,
                ColSectionOutput,
                previous_response_id=previous_response_id,
                validate=validate_col_section,
            )
        except Exception as e:
            logger.error("Error in extract_col_section: %s", e)
            raise
