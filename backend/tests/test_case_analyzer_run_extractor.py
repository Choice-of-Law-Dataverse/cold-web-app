"""Tests for the shared extractor agent construction in the case analyzer runner."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.items import ToolCallItem

from app.case_analyzer.config import get_model
from app.case_analyzer.runner import run_extractor
from app.case_analyzer.tools.document_nav import NAV_TOOLS, DocumentContext
from app.case_analyzer.tools.models import CaseCitationOutput, ThemeClassificationOutput


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
async def test_builds_agent_from_task_and_runs_it() -> None:
    runner = AsyncMock(return_value=_run_result("output", "response-1", ("search",)))
    context = DocumentContext(draft_id=1, text="decision")

    with (
        patch("app.case_analyzer.runner.Runner.run", runner),
        patch("app.case_analyzer.runner.get_openai_client", return_value=MagicMock()),
    ):
        result = await run_extractor(
            name="ThemeClassifier",
            task="themes",
            output_type=ThemeClassificationOutput,
            instructions="system prompt",
            prompt="extract",
            context=context,
        )

    assert result.output == "output"
    assert result.response_id == "response-1"
    assert result.tool_names == ("search",)
    runner.assert_awaited_once()
    call = runner.await_args
    assert call is not None
    agent = cast(Any, call.args[0])
    assert agent.name == "ThemeClassifier"
    assert agent.instructions == "system prompt"
    assert agent.output_type is ThemeClassificationOutput
    assert agent.tools == NAV_TOOLS
    assert agent.model.model == get_model("themes")
    assert call.kwargs["input"] == "extract"
    assert call.kwargs["context"] is context


@pytest.mark.asyncio
async def test_honours_custom_tools_and_validator() -> None:
    runner = AsyncMock(
        side_effect=[
            _run_result("first", "response-1"),
            _run_result("second", "response-2", ("search",)),
        ]
    )

    with (
        patch("app.case_analyzer.runner.Runner.run", runner),
        patch("app.case_analyzer.runner.get_openai_client", return_value=MagicMock()),
    ):
        result = await run_extractor(
            name="CaseCitationExtractor",
            task="case_citation",
            output_type=CaseCitationOutput,
            instructions="instructions",
            prompt=[{"role": "user", "content": "extract"}],
            context=DocumentContext(draft_id=1, text="decision"),
            validate=_require_search,
            tools=[],
        )

    assert result.output == "second"
    assert result.tool_names == ("search",)
    assert runner.await_count == 2
    agent = cast(Any, runner.await_args_list[0].args[0])
    assert agent.tools == []
    assert agent.model.model == get_model("case_citation")
    assert runner.await_args_list[0].kwargs["input"] == [{"role": "user", "content": "extract"}]
