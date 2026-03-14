import logging

import logfire
from agents import Agent, Runner, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from .models import CaseCitationOutput

logger = logging.getLogger(__name__)


async def extract_case_citation(
    text: str,
    legal_system: str,
    jurisdiction: str,
) -> CaseCitationOutput:
    """Extract case citation from court decision text."""
    with logfire.span("case_citation"):
        instructions = "Extract the case citation from the provided court decision text. Provide the citation in an academic format, including all necessary details such as case name, reporter, court, and year. If the citation is not explicitly mentioned in the text, infer it based on context. Ensure accuracy and clarity in the citation format. Tailor the citation style to the legal system and jurisdiction specified."

        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": f"Jusdiction: {jurisdiction}\nLegal System: {legal_system}",
            },
            {
                "role": "user",
                "content": text,
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
        run_result = await Runner.run(agent, prompt)
        result = run_result.final_output_as(CaseCitationOutput)

        return result
