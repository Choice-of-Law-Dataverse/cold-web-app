"""Thin runner wrapper for case analyzer agents."""

import logging
from typing import Any

from agents import Agent, Runner
from agents.items import ToolCallItem

from .tools.document_nav import DocumentContext
from .tools.models import StepResult
from .validation import ValidatorFn

logger = logging.getLogger(__name__)

_MAX_VALIDATION_ATTEMPTS = 2


class OutputValidationError(RuntimeError):
    """Raised when an agent cannot produce an evidence-backed valid output."""


def _tool_names(new_items: list[Any]) -> frozenset[str]:
    return frozenset(item.tool_name for item in new_items if isinstance(item, ToolCallItem) and item.tool_name is not None)


def _retry_prompt(validation_error: str) -> str:
    return (
        "Your previous response could not be accepted for this reason:\n"
        f"{validation_error}\n\n"
        "Correct the response now. Use the document navigation tools when requested, base the answer only on the court "
        "decision, and return the required structured output."
    )


async def run_agent(
    agent: Agent[Any],
    *,
    input: str | list[Any],
    context: DocumentContext,
    validate: ValidatorFn | None = None,
) -> StepResult[Any]:
    current_input = input
    response_id: str | None = None
    used_tools: frozenset[str] = frozenset()

    for attempt in range(_MAX_VALIDATION_ATTEMPTS):
        result = await Runner.run(
            agent,
            input=current_input,
            context=context,
            previous_response_id=response_id,
        )
        response_id = result.last_response_id
        used_tools |= _tool_names(result.new_items)

        validation_error = validate(result.final_output, used_tools) if validate else None
        if validation_error is None:
            return StepResult(
                output=result.final_output,
                response_id=response_id,
                tool_names=tuple(sorted(used_tools)),
            )

        logger.warning(
            "Validation failed for %s on attempt %d: %s",
            agent.name,
            attempt + 1,
            validation_error,
        )
        if attempt + 1 < _MAX_VALIDATION_ATTEMPTS:
            current_input = _retry_prompt(validation_error)
            continue
        raise OutputValidationError(f"{agent.name} failed output validation: {validation_error}")

    raise AssertionError("validation attempt loop exited unexpectedly")
