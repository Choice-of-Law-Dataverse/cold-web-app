import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..quote_guardrail import verify_supporting_quotes
from ..runner import run_agent
from ..utils import filter_themes_by_list, generate_system_prompt
from .document_nav import (
    DocumentContext,
    get_paragraph_containing,
    list_headings,
    read_head,
    read_section,
    read_tail,
    read_window,
    search,
)
from .models import ColIssueOutput, ColSectionOutput, StepResult, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def extract_col_issue(
    doc_ctx: DocumentContext,
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

        prompt = COL_ISSUE_PROMPT.format(col_section=str(col_section_output), classification_definitions=themes_definitions)
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="ColIssueExtractor",
            instructions=system_prompt,
            output_type=ColIssueOutput,
            tools=[search, get_paragraph_containing, list_headings, read_section, read_window, read_head, read_tail],
            output_guardrails=[verify_supporting_quotes],
            model=OpenAIResponsesModel(
                model=get_model("col_issue"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
