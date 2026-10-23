import logging

import logfire

from ..prompts import get_prompt_module
from ..runner import run_extractor
from ..utils import generate_system_prompt
from ..validation import validate_dissenting_opinions
from .document_nav import DocumentContext
from .models import (
    ColIssueOutput,
    ColSectionOutput,
    DissentingOpinionsOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_dissenting_opinions(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
) -> StepResult[DissentingOpinionsOutput]:
    with logfire.span("dissenting_opinions"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        prompt_template = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = prompt_template.format(
            col_section=str(col_section_output),
            classification=themes,
            col_issue=col_issue,
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        return await run_extractor(
            name="DissentingOpinionsExtractor",
            task="dissenting_opinions",
            output_type=DissentingOpinionsOutput,
            instructions=system_prompt,
            prompt=prompt,
            context=doc_ctx,
            validate=validate_dissenting_opinions,
        )
