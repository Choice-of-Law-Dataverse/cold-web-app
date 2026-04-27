"""Thin runner wrapper for case analyzer agents."""

import logging
from typing import Any

from agents import Agent, Runner

from .tools.document_nav import DocumentContext
from .tools.models import StepResult

logger = logging.getLogger(__name__)


async def run_agent(
    agent: Agent[Any],
    *,
    input: str | list[Any],
    context: DocumentContext,
    previous_response_id: str | None = None,
) -> StepResult[Any]:
    result = await Runner.run(
        agent,
        input=input,
        context=context,
        previous_response_id=previous_response_id,
    )
    return StepResult(output=result.final_output, response_id=result.last_response_id)
