"""Retry-aware runner for case analyzer agents with output validation."""

import logging
from collections.abc import Callable
from typing import Any

from agents import Agent, Runner, TResponseInputItem

from .tools.models import ConfidenceReasoningModel, StepResult

logger = logging.getLogger(__name__)

type ValidatorFn = Callable[[Any], str | None]

LOW_CONFIDENCE_PROMPT = (
    "Your previous analysis had low confidence. "
    "Re-examine the court decision text more carefully and provide a more thorough, well-supported analysis."
)


async def run_with_retry[T: ConfidenceReasoningModel](
    agent: Agent[None],
    prompt: str | list[TResponseInputItem],
    output_type: type[T],
    previous_response_id: str | None = None,
    validate: ValidatorFn | None = None,
) -> StepResult[T]:
    run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
    result = run_result.final_output_as(output_type)
    response_id = run_result.last_response_id

    validation_error = validate(result) if validate else None
    needs_retry = False
    retry_prompt: str = LOW_CONFIDENCE_PROMPT

    if validation_error:
        needs_retry = True
        retry_prompt = validation_error
        logger.warning("Validation failed for %s: %s — retrying", agent.name, validation_error)
    elif result.confidence == "low":
        needs_retry = True
        logger.info("Low confidence from %s — retrying", agent.name)

    if needs_retry:
        retry_result = await Runner.run(agent, retry_prompt, previous_response_id=response_id)
        result = retry_result.final_output_as(output_type)
        response_id = retry_result.last_response_id

    return StepResult(output=result, response_id=response_id)
