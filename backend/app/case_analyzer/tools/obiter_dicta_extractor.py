import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import generate_system_prompt
from ..validation import validate_obiter_dicta
from .document_nav import NAV_TOOLS, DocumentContext
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
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("obiter_dicta"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(
            agent,
            input=prompt,
            context=doc_ctx,
            validate=validate_obiter_dicta,
        )
