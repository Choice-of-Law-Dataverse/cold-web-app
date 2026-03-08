import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..prompts import get_prompt_module
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

        prompt = FACTS_PROMPT.format(text=text, col_section=str(col_section_output))
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
        run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
        result = run_result.final_output_as(RelevantFactsOutput)

        return StepResult(output=result, response_id=run_result.last_response_id)
