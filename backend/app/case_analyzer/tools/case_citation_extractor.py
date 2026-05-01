import logging

import logfire
from agents import Agent, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..runner import run_agent
from .document_nav import DocumentContext, read_head, search
from .models import CaseCitationOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_case_citation(
    doc_ctx: DocumentContext,
    legal_system: str,
    jurisdiction: str,
    previous_response_id: str | None = None,
) -> StepResult[CaseCitationOutput]:
    """Extract case citation from court decision text."""
    with logfire.span("case_citation"):
        instructions = (
            "Extract the canonical case citation as it appears in the court decision. "
            "Use the document's own citation format and language verbatim — do not translate, "
            "expand, or reformat court names, abbreviations (BGE, OGH, BGH, EWHC, etc.), or "
            "docket numbers. Prefer the short canonical identifier (e.g., 'BGE 138 III 232') "
            "over the full case header with parties, judges, and dates. "
            "If no citation is explicitly present in the text, return 'NA' — do not infer or fabricate."
        )

        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": f"Jusdiction: {jurisdiction}\nLegal System: {legal_system}",
            },
        ]

        agent = Agent[DocumentContext](
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            tools=[read_head, search],
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
