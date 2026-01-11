import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analyzer.config import get_model, get_openai_client
from app.case_analyzer.models.analysis_models import ColSectionOutput, PILProvisionsOutput
from app.case_analyzer.prompts.prompt_selector import get_prompt_module
from app.case_analyzer.utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


async def extract_pil_provisions(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
):
    """
    Extract PIL provisions from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")

    Returns:
        PILProvisionsOutput: Extracted provisions with confidence and reasoning
    """
    with logfire.span("pil_provisions"):
        PIL_PROVISIONS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).PIL_PROVISIONS_PROMPT

        prompt = PIL_PROVISIONS_PROMPT.format(text=text, col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("pil_provisions"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt)
        result = run_result.final_output_as(PILProvisionsOutput)

        return result
