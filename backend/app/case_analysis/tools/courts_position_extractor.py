import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analysis.config import get_model, get_openai_client
from app.case_analysis.models.analysis_models import ColIssueOutput, ColSectionOutput, CourtsPositionOutput
from app.case_analysis.models.classification_models import ThemeClassificationOutput
from app.case_analysis.prompts.prompt_selector import get_prompt_module
from app.case_analysis.utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


async def extract_courts_position(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
):
    """
    Extract court's position from court decision.

    Args:
        text: Full court decision text
        col_section_output: Extracted Choice of Law sections
        legal_system: Legal system type (e.g., "Civil-law jurisdiction")
        jurisdiction: Precise jurisdiction (e.g., "Switzerland")
        themes_output: Classified themes output
        col_issue_output: Extracted Choice of Law issue

    Returns:
        CourtsPositionOutput: Extracted position with confidence and reasoning
    """
    with logfire.span("courts_position"):
        COURTS_POSITION_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COURTS_POSITION_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = COURTS_POSITION_PROMPT.format(
            col_issue=col_issue, text=text, col_section=str(col_section_output), classification=themes
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="CourtsPositionExtractor",
            instructions=system_prompt,
            output_type=CourtsPositionOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("courts_position"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt)
        result = run_result.final_output_as(CourtsPositionOutput)

        return result
