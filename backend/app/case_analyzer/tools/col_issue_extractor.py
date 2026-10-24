import logging

import logfire

from ..prompts import get_prompt_module
from ..runner import run_extractor
from ..utils import filter_themes_by_list, generate_system_prompt
from ..validation import validate_col_issue
from .document_nav import DocumentContext
from .models import ColIssueOutput, ColSectionOutput, StepResult, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def extract_col_issue(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
) -> StepResult[ColIssueOutput]:
    with logfire.span("col_issue"):
        COL_ISSUE_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).COL_ISSUE_PROMPT

        themes = themes_output.themes
        themes_definitions = filter_themes_by_list(themes)

        prompt = COL_ISSUE_PROMPT.format(col_section=str(col_section_output), classification_definitions=themes_definitions)
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        return await run_extractor(
            name="ColIssueExtractor",
            task="col_issue",
            output_type=ColIssueOutput,
            instructions=system_prompt,
            prompt=prompt,
            context=doc_ctx,
            validate=validate_col_issue,
        )
