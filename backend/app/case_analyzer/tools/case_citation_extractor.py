import logging

import logfire
from agents import Agent, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_case_citation
from ..runner import TEXT_REFERENCE, run_with_retry
from .models import CaseCitationOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_case_citation(
    text: str,
    legal_system: str,
    jurisdiction: str,
    previous_response_id: str | None = None,
) -> StepResult[CaseCitationOutput]:
    """Extract case citation from court decision text."""
    with logfire.span("case_citation"):
        instructions = "Extract the case citation from the provided court decision text. Provide the citation in an academic format, including all necessary details such as case name, reporter, court, and year. If the citation is not explicitly mentioned in the text, infer it based on context. Ensure accuracy and clarity in the citation format. Tailor the citation style to the legal system and jurisdiction specified."

        effective_text = text if previous_response_id is None else TEXT_REFERENCE
        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": f"Jusdiction: {jurisdiction}\nLegal System: {legal_system}",
            },
            {
                "role": "user",
                "content": effective_text,
            },
        ]

        agent = Agent(
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            CaseCitationOutput,
            previous_response_id=previous_response_id,
            validate=validate_case_citation,
        )
