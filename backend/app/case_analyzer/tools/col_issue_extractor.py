import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import filter_themes_by_list, generate_system_prompt
from .models import ColIssueOutput, ColSectionOutput, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def extract_col_issue(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
):
    """
    Extract Choice of Law issue from court decision.

    Args:
        text: Full court decision text
        col_section_output: Extracted Choice of Law sections
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        themes_output: Classified themes output

    Returns:
        ColIssueOutput: Extracted issue with confidence and reasoning
    """
    with logfire.span("col_issue"):
        COL_ISSUE_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COL_ISSUE_PROMPT

        themes = themes_output.themes
        themes_definitions = filter_themes_by_list(themes)

        prompt = COL_ISSUE_PROMPT.format(
            text=text, col_section=str(col_section_output), classification_definitions=themes_definitions
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("col_issue"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt)
        result = run_result.final_output_as(ColIssueOutput)

        return result
