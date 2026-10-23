import logging

import logfire

from ..prompts import get_prompt_module
from ..runner import run_extractor
from ..utils import generate_system_prompt
from ..validation import validate_relevant_facts
from .document_nav import DocumentContext
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

        return await run_extractor(
            name="RelevantFactsExtractor",
            task="relevant_facts",
            output_type=RelevantFactsOutput,
            instructions=system_prompt,
            prompt=prompt,
            context=doc_ctx,
            validate=validate_relevant_facts,
        )
