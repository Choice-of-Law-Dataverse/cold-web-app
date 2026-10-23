import logging

import logfire

from ..prompts import get_prompt_module
from ..runner import run_extractor
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from ..validation import validate_themes
from .document_nav import DocumentContext
from .models import StepResult, ThemeClassificationOutput

logger = logging.getLogger(__name__)


async def classify_themes(
    doc_ctx: DocumentContext,
    col_section: str,
    legal_system: str,
    jurisdiction: str | None,
) -> StepResult[ThemeClassificationOutput]:
    with logfire.span("themes"):
        PIL_THEME_PROMPT = get_prompt_module(legal_system, "theme", jurisdiction).PIL_THEME_PROMPT

        prompt = PIL_THEME_PROMPT.format(col_section=col_section, themes_table=THEMES_TABLE_STR)
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        try:
            return await run_extractor(
                name="ThemeClassifier",
                task="themes",
                output_type=ThemeClassificationOutput,
                instructions=system_prompt,
                prompt=prompt,
                context=doc_ctx,
                validate=validate_themes,
            )
        except Exception as e:
            logger.error("Error during theme classification: %s", e)
            raise
