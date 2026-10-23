import logging

import logfire

from ..prompts import get_prompt_module
from ..runner import run_extractor
from ..utils import generate_system_prompt
from ..validation import validate_pil_provisions
from .document_nav import DocumentContext
from .models import ColSectionOutput, PILProvisionsOutput, StepResult

logger = logging.getLogger(__name__)


async def extract_pil_provisions(
    doc_ctx: DocumentContext,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
) -> StepResult[PILProvisionsOutput]:
    with logfire.span("pil_provisions"):
        PIL_PROVISIONS_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).PIL_PROVISIONS_PROMPT

        prompt = PIL_PROVISIONS_PROMPT.format(col_section=str(col_section_output))
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        return await run_extractor(
            name="PILProvisionsExtractor",
            task="pil_provisions",
            output_type=PILProvisionsOutput,
            instructions=system_prompt,
            prompt=prompt,
            context=doc_ctx,
            validate=validate_pil_provisions,
        )
