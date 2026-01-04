import asyncio
import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analysis.config import get_model, get_openai_client
from app.case_analysis.models.analysis_models import ColSectionOutput, RelevantFactsOutput
from app.case_analysis.prompts.prompt_selector import get_prompt_module
from app.case_analysis.utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


def extract_relevant_facts(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
):
    """
    Extract relevant facts from court decision.

    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")

    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    with logfire.span("relevant_facts"):
        FACTS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(text=text, col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("relevant_facts"),
                openai_client=get_openai_client(),
            ),
        )
        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(RelevantFactsOutput)

        return result
