import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_col_issue
from ..prompts import get_prompt_module
from ..runner import TEXT_REFERENCE, run_with_retry
from ..utils import filter_themes_by_list, generate_system_prompt
from .models import ColIssueOutput, ColSectionOutput, StepResult, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def extract_col_issue(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    previous_response_id: str | None = None,
) -> StepResult[ColIssueOutput]:
    with logfire.span("col_issue"):
        COL_ISSUE_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COL_ISSUE_PROMPT

        themes = themes_output.themes
        themes_definitions = filter_themes_by_list(themes)

        effective_text = text if previous_response_id is None else TEXT_REFERENCE
        prompt = COL_ISSUE_PROMPT.format(
            text=effective_text, col_section=str(col_section_output), classification_definitions=themes_definitions
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent(
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            model=OpenAIResponsesModel(
                model=get_model("col_issue"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            ColIssueOutput,
            previous_response_id=previous_response_id,
            validate=validate_col_issue,
        )
