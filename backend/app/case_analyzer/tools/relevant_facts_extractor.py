import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
from ..quote_guardrail import verify_supporting_quotes
from ..runner import run_agent
from ..utils import generate_system_prompt
from .document_nav import DocumentContext, get_paragraph_containing, read_window, search
from .models import ColSectionOutput, RelevantFactsOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_relevant_facts(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    previous_response_id: str | None = None,
) -> StepResult[RelevantFactsOutput]:
    with logfire.span("relevant_facts"):
        FACTS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).FACTS_PROMPT

        prompt = FACTS_PROMPT.format(col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            tools=[search, read_window, get_paragraph_containing],
            output_guardrails=[verify_supporting_quotes],
            model=OpenAIResponsesModel(
                model=get_model("relevant_facts"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
