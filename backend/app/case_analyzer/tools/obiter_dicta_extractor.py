import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..utils import generate_system_prompt
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    ObiterDictaOutput,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_obiter_dicta(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
) -> ObiterDictaOutput:
    """Extract obiter dicta commentary for Common Law or India workflows."""
    with logfire.span("obiter_dicta"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        prompt_template = prompt_module.COURTS_POSITION_OBITER_DICTA_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = prompt_template.format(
            text=text,
            col_section=str(col_section_output),
            classification=themes,
            col_issue=col_issue,
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="ObiterDictaExtractor",
            instructions=system_prompt,
            output_type=ObiterDictaOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("obiter_dicta"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt)
        return run_result.final_output_as(ObiterDictaOutput)
