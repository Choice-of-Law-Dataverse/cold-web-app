import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import generate_system_prompt
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_courts_position(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
    previous_response_id: str | None = None,
) -> StepResult[CourtsPositionOutput]:
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
            model=OpenAIResponsesModel(
                model=get_model("courts_position"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
        result = run_result.final_output_as(CourtsPositionOutput)

        return StepResult(output=result, response_id=run_result.last_response_id)
