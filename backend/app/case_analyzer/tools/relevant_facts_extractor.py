import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_relevant_facts
from ..prompts import get_prompt_module
from ..runner import TEXT_REFERENCE, run_with_retry
from ..utils import generate_system_prompt
from .models import ColSectionOutput, RelevantFactsOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_relevant_facts(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    previous_response_id: str | None = None,
) -> StepResult[RelevantFactsOutput]:
    with logfire.span("relevant_facts"):
        FACTS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).FACTS_PROMPT

        effective_text = text if previous_response_id is None else TEXT_REFERENCE
        prompt = FACTS_PROMPT.format(text=effective_text, col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="RelevantFactsExtractor",
            instructions=system_prompt,
            output_type=RelevantFactsOutput,
            model=OpenAIResponsesModel(
                model=get_model("relevant_facts"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            RelevantFactsOutput,
            previous_response_id=previous_response_id,
            validate=validate_relevant_facts,
        )
