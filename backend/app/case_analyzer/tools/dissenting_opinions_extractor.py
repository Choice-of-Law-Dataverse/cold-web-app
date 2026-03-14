import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_dissenting_opinions
from ..prompts import get_prompt_module
from ..runner import TEXT_REFERENCE, run_with_retry
from ..utils import generate_system_prompt
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    DissentingOpinionsOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_dissenting_opinions(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
    previous_response_id: str | None = None,
) -> StepResult[DissentingOpinionsOutput]:
    with logfire.span("dissenting_opinions"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        prompt_template = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        effective_text = text if previous_response_id is None else TEXT_REFERENCE
        prompt = prompt_template.format(
            text=effective_text,
            col_section=str(col_section_output),
            classification=themes,
            col_issue=col_issue,
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent(
            name="DissentingOpinionsExtractor",
            instructions=system_prompt,
            output_type=DissentingOpinionsOutput,
            model=OpenAIResponsesModel(
                model=get_model("dissenting_opinions"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            DissentingOpinionsOutput,
            previous_response_id=previous_response_id,
            validate=validate_dissenting_opinions,
        )
