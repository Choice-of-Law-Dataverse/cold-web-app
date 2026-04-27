"""Output guardrail that verifies supporting_quotes appear verbatim in the source document."""

import re

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail
from pydantic import BaseModel

from .tools.document_nav import DocumentContext


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


@output_guardrail
async def verify_supporting_quotes(
    ctx: RunContextWrapper[DocumentContext],
    _agent: Agent,  # type: ignore[type-arg]
    output: BaseModel,
) -> GuardrailFunctionOutput:
    """Reject any output whose supporting_quotes are not found verbatim in the source text."""
    quotes: list[str] = getattr(output, "supporting_quotes", None) or []
    normalized_text = _normalize(ctx.context.text)
    missing = [q for q in quotes if _normalize(q) not in normalized_text]
    return GuardrailFunctionOutput(
        output_info={"missing_quotes": missing},
        tripwire_triggered=bool(missing),
    )
