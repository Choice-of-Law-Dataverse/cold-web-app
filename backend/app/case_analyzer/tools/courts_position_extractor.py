import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_courts_position
from ..prompts import get_prompt_module
from ..runner import TEXT_REFERENCE, run_with_retry
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

        effective_text = text if previous_response_id is None else TEXT_REFERENCE
        prompt = COURTS_POSITION_PROMPT.format(
            col_issue=col_issue, text=effective_text, col_section=str(col_section_output), classification=themes
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent(
            name="CourtsPositionExtractor",
            instructions=system_prompt,
            output_type=CourtsPositionOutput,
            model=OpenAIResponsesModel(
                model=get_model("courts_position"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            CourtsPositionOutput,
            previous_response_id=previous_response_id,
            validate=validate_courts_position,
        )
