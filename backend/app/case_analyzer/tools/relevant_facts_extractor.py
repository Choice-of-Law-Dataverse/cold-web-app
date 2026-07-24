import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import generate_system_prompt
from ..validation import validate_relevant_facts
from .document_nav import NAV_TOOLS, DocumentContext
from .models import ColSectionOutput, RelevantFactsOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_relevant_facts(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
) -> StepResult[RelevantFactsOutput]:
    with logfire.span("relevant_facts"):
        FACTS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            tools=NAV_TOOLS,
            model=OpenAIResponsesModel(
                model=get_model("relevant_facts"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(
            agent,
            input=prompt,
            context=doc_ctx,
            validate=validate_relevant_facts,
        )
