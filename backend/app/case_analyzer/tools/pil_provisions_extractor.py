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
from .models import ColSectionOutput, PILProvisionsOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_pil_provisions(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    previous_response_id: str | None = None,
) -> StepResult[PILProvisionsOutput]:
    with logfire.span("pil_provisions"):
        PIL_PROVISIONS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).PIL_PROVISIONS_PROMPT

        prompt = PIL_PROVISIONS_PROMPT.format(col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        agent = Agent[DocumentContext](
            name="PILProvisionsExtractor",
            instructions=system_prompt,
            output_type=PILProvisionsOutput,
            tools=[search, read_window, get_paragraph_containing],
            output_guardrails=[verify_supporting_quotes],
            model=OpenAIResponsesModel(
                model=get_model("pil_provisions"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
