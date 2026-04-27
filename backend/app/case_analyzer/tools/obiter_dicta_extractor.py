import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..quote_guardrail import verify_supporting_quotes
from ..runner import run_agent
from ..utils import generate_system_prompt
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
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    ObiterDictaOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_obiter_dicta(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
    previous_response_id: str | None = None,
) -> StepResult[ObiterDictaOutput]:
    with logfire.span("obiter_dicta"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        prompt_template = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = prompt_template.format(
            col_section=str(col_section_output),
            classification=themes,
            col_issue=col_issue,
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="ObiterDictaExtractor",
            instructions=system_prompt,
            output_type=ObiterDictaOutput,
            tools=[search, get_paragraph_containing, list_headings, read_section, read_window, read_head, read_tail],
            output_guardrails=[verify_supporting_quotes],
            model=OpenAIResponsesModel(
                model=get_model("obiter_dicta"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
