import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts.col_section import COL_SECTION_PROMPT
from ..runner import run_agent
from ..utils import generate_system_prompt
from .document_nav import NAV_TOOLS, DocumentContext
from .models import ColSectionOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_col_section(
    doc_ctx: DocumentContext,
    previous_response_id: str | None = None,
) -> StepResult[ColSectionOutput]:
    with logfire.span("col_section"):
        agent = Agent[DocumentContext](
            name="ColSectionExtractor",
            instructions=generate_system_prompt(),
            output_type=ColSectionOutput,
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("col_section"),
                openai_client=get_openai_client(),
            ),
        )

        try:
            return await run_agent(agent, input=COL_SECTION_PROMPT, context=doc_ctx, previous_response_id=previous_response_id)
        except Exception as e:
            logger.error("Error in extract_col_section: %s", e)
            raise
