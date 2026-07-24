"""Tests for evidence-aware case analyzer agent execution."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.items import ToolCallItem

from app.case_analyzer.runner import OutputValidationError, run_agent
from app.case_analyzer.tools.document_nav import DocumentContext


def _run_result(output: object, response_id: str, tool_names: tuple[str, ...] = ()) -> SimpleNamespace:
    agent = MagicMock()
    items = [
        ToolCallItem(
            agent=agent,
            raw_item={"type": "function_call", "name": name, "call_id": f"call-{i}", "arguments": "{}"},
        )
        for i, name in enumerate(tool_names)
    ]
    return SimpleNamespace(final_output=output, last_response_id=response_id, new_items=items)


def _require_search(_output: object, tool_names: frozenset[str]) -> str | None:
    return None if "search" in tool_names else "Search the document before answering."


@pytest.mark.asyncio
async def test_retries_with_validation_feedback_and_accumulates_tool_evidence() -> None:
    runner = AsyncMock(
        side_effect=[
            _run_result("first", "response-1"),
            _run_result("second", "response-2", ("search",)),
        ]
    )
    agent = cast(Any, MagicMock(name="Extractor"))

    with patch("app.case_analyzer.runner.Runner.run", runner):
        result = await run_agent(
            agent,
            input="extract",
            context=DocumentContext(draft_id=1, text="decision"),
            validate=_require_search,
        )

    assert result.output == "second"
    assert result.response_id == "response-2"
    assert result.tool_names == ("search",)
    assert runner.await_count == 2
    second_call = runner.await_args_list[1]
    assert second_call.kwargs["previous_response_id"] == "response-1"
    assert "Search the document" in second_call.kwargs["input"]


@pytest.mark.asyncio
async def test_raises_after_second_invalid_response() -> None:
    runner = AsyncMock(
        side_effect=[
            _run_result("first", "response-1"),
            _run_result("second", "response-2"),
        ]
    )
    agent = cast(Any, MagicMock(name="Extractor"))

    with (
        patch("app.case_analyzer.runner.Runner.run", runner),
        pytest.raises(OutputValidationError, match="failed output validation"),
    ):
        await run_agent(
            agent,
            input="extract",
            context=DocumentContext(draft_id=1, text="decision"),
            validate=_require_search,
        )


@pytest.mark.asyncio
async def test_runner_without_validator_does_not_retry() -> None:
    runner = AsyncMock(return_value=_run_result("output", "response-1", ("read_head",)))
    agent = cast(Any, MagicMock(name="Extractor"))

    with patch("app.case_analyzer.runner.Runner.run", runner):
        result = await run_agent(
            agent,
            input="extract",
            context=DocumentContext(draft_id=1, text="decision"),
        )

    assert result.output == "output"
    assert result.tool_names == ("read_head",)
    runner.assert_awaited_once()
