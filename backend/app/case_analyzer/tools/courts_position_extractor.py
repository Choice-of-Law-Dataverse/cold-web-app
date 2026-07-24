import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import generate_system_prompt
from ..validation import validate_courts_position
from .document_nav import NAV_TOOLS, DocumentContext
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_courts_position(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
) -> StepResult[CourtsPositionOutput]:
    with logfire.span("courts_position"):
        COURTS_POSITION_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COURTS_POSITION_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = COURTS_POSITION_PROMPT.format(col_issue=col_issue, col_section=str(col_section_output), classification=themes)
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="CourtsPositionExtractor",
            instructions=system_prompt,
            output_type=CourtsPositionOutput,
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("courts_position"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(
            agent,
            input=prompt,
            context=doc_ctx,
            validate=validate_courts_position,
        )
