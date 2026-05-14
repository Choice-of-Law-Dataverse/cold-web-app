import logging

import logfire
from agents import Agent, TResponseInputItem
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..runner import run_agent
from .document_nav import (
    DocumentContext,
    get_paragraph_containing,
    list_headings,
    read_head,
    read_section,
    read_tail,
    read_window,
    search,
)
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
            "Citations typically appear in the first or last page; start with read_head or "
            "read_tail, and use search for known patterns (BGE, OGH, BGH, EWHC, etc.). "
            "Use the document's own citation format and language verbatim — do not translate, "
            "expand, or reformat court names, abbreviations, or docket numbers. Prefer the "
            "short canonical identifier (e.g., 'BGE 138 III 232') over the full case header "
            "with parties, judges, and dates. "
            "If no citation is explicitly present after searching, return 'NA' — do not infer "
            "or fabricate. "
            "The reasoning field must describe HOW the citation was located in the source "
            "(e.g., 'Found on page 1 in the docket header'); do not write meta-commentary "
            "about the task, your tools, or your capabilities."
        )

        prompt: list[TResponseInputItem] = [
            {
                "role": "user",
                "content": f"Jurisdiction: {jurisdiction}\nLegal System: {legal_system}",
            },
        ]

        agent = Agent[DocumentContext](
            name="CaseCitationExtractor",
            instructions=instructions,
            output_type=CaseCitationOutput,
            tools=[search, get_paragraph_containing, list_headings, read_section, read_window, read_head, read_tail],
            model=OpenAIResponsesModel(
                model=get_model("case_citation"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_agent(agent, input=prompt, context=doc_ctx, previous_response_id=previous_response_id)
