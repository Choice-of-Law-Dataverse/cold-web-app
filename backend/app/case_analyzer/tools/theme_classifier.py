import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from ..validation import validate_themes
from .document_nav import NAV_TOOLS, DocumentContext
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
            agent = Agent[DocumentContext](
                name="ThemeClassifier",
                instructions=system_prompt,
                output_type=ThemeClassificationOutput,
                tools=NAV_TOOLS,
                model=OpenAIResponsesModel(
                    model=get_model("themes"),
                    openai_client=get_openai_client(),
                ),
            )
            return await run_agent(
                agent,
                input=prompt,
                context=doc_ctx,
                validate=validate_themes,
            )
        except Exception as e:
            logger.error("Error during theme classification: %s", e)
            raise
