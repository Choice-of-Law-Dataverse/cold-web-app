import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analysis.config import get_model, get_openai_client
from app.case_analysis.models.analysis_models import ColSectionOutput
from app.case_analysis.prompts.prompt_selector import get_prompt_module
from app.case_analysis.utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


async def extract_col_section(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
):
    """
    Extract Choice of Law section from court decision text.

    Args:
        text: Full court decision text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")


    Returns:
        ColSectionOutput: Extracted sections with confidence and reasoning
    """
    with logfire.span("col_section"):
        COL_SECTION_PROMPT = get_prompt_module(legal_system, "col_section", jurisdiction).COL_SECTION_PROMPT

        prompt = COL_SECTION_PROMPT.format(text=text)

        system_prompt = generate_system_prompt(legal_system, jurisdiction, "col_section")

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
            logger.error("Error in extract_col_section: %s", e)
            raise
