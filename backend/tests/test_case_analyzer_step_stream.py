"""Tests for the step event stream emitted by analyze_case_streaming."""

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from app.case_analyzer.service import analyze_case_streaming
from app.case_analyzer.steps import NON_ABORTING_STEPS, AnalysisStep
from app.case_analyzer.tools.models import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    JurisdictionOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    StepResult,
    ThemeClassificationOutput,
)

_SERVICE = "app.case_analyzer.service"

_CIVIL_JURISDICTION = JurisdictionOutput(
    legal_system_type="Civil-law jurisdiction",
    precise_jurisdiction="Switzerland",
    jurisdiction_code="CH",
    confidence="high",
    reasoning="Swiss court.",
)


def _step(output: object) -> StepResult[Any]:
    return StepResult(output=output, response_id="resp")


def _fakes() -> dict[str, AsyncMock]:
    return {
        "detect_jurisdiction": AsyncMock(return_value=_CIVIL_JURISDICTION),
        "extract_col_section": AsyncMock(
            return_value=_step(ColSectionOutput(col_sections=["Art. 3 applies."], confidence="high", reasoning="ok"))
        ),
        "classify_themes": AsyncMock(
            return_value=_step(ThemeClassificationOutput(themes=["Party autonomy"], confidence="high", reasoning="ok"))
        ),
        "extract_case_citation": AsyncMock(
            return_value=_step(
                CaseCitationOutput(
                    case_citation="BGE 123 III 456",
                    source_text="BGE 123 III 456",
                    source_location="document beginning",
                    identifier_type="reporter citation",
                    confidence="high",
                    reasoning="ok",
                )
            )
        ),
        "extract_relevant_facts": AsyncMock(
            return_value=_step(
                RelevantFactsOutput(relevant_facts="The parties signed a contract.", confidence="high", reasoning="ok")
            )
        ),
        "extract_pil_provisions": AsyncMock(
            return_value=_step(PILProvisionsOutput(pil_provisions=["Art. 3 Rome I"], confidence="high", reasoning="ok"))
        ),
        "extract_col_issue": AsyncMock(
            return_value=_step(ColIssueOutput(col_issue="Which law governs?", confidence="high", reasoning="ok"))
        ),
        "extract_courts_position": AsyncMock(
            return_value=_step(CourtsPositionOutput(courts_position="Swiss law applies.", confidence="high", reasoning="ok"))
        ),
        "extract_abstract": AsyncMock(
            return_value=_step(AbstractOutput(abstract="This case concerns CoL.", confidence="high", reasoning="ok"))
        ),
    }


async def _collect(fakes: dict[str, AsyncMock]) -> list[dict[str, Any]]:
    with patch.multiple(_SERVICE, **fakes):
        return [event async for event in analyze_case_streaming("decision text", draft_id=1)]


def _sequence(events: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [(event["step"], event["status"]) for event in events]


@pytest.mark.asyncio
async def test_successful_civil_law_run_emits_the_expected_sequence() -> None:
    events = await _collect(_fakes())

    assert _sequence(events) == [
        ("jurisdiction_detection", "in_progress"),
        ("col_extraction", "in_progress"),
        ("jurisdiction_detection", "completed"),
        ("col_extraction", "completed"),
        ("theme_classification", "in_progress"),
        ("case_citation", "in_progress"),
        ("relevant_facts", "in_progress"),
        ("pil_provisions", "in_progress"),
        ("theme_classification", "completed"),
        ("case_citation", "completed"),
        ("relevant_facts", "completed"),
        ("pil_provisions", "completed"),
        ("col_issue", "in_progress"),
        ("col_issue", "completed"),
        ("courts_position", "in_progress"),
        ("courts_position", "completed"),
        ("abstract", "in_progress"),
        ("abstract", "completed"),
        ("analysis_complete", "completed"),
    ]


@pytest.mark.asyncio
async def test_events_serialise_with_plain_step_strings() -> None:
    events = await _collect(_fakes())

    for event in events:
        assert json.loads(json.dumps(event))["step"] == event["step"]
    assert json.dumps(events[0]) == '{"step": "jurisdiction_detection", "status": "in_progress"}'
    assert all(isinstance(event["step"], AnalysisStep) for event in events)


@pytest.mark.asyncio
async def test_failing_case_citation_emits_error_and_run_completes() -> None:
    fakes = _fakes()
    fakes["extract_case_citation"] = AsyncMock(side_effect=RuntimeError("citation boom"))

    events = await _collect(fakes)

    assert ("case_citation", "error") in _sequence(events)
    assert ("case_citation", "completed") not in _sequence(events)
    error_event = next(event for event in events if event["status"] == "error")
    assert error_event["error"] == "citation boom"
    assert _sequence(events)[-1] == ("analysis_complete", "completed")
    for step in ("theme_classification", "relevant_facts", "pil_provisions", "col_issue", "courts_position", "abstract"):
        assert (step, "completed") in _sequence(events)


@pytest.mark.asyncio
async def test_failing_relevant_facts_stops_the_run() -> None:
    fakes = _fakes()
    fakes["extract_relevant_facts"] = AsyncMock(side_effect=RuntimeError("facts boom"))

    events = await _collect(fakes)

    assert _sequence(events)[-1] == ("relevant_facts", "error")
    steps = {step for step, _ in _sequence(events)}
    assert "analysis_complete" not in steps
    assert "col_issue" not in steps
    fakes["extract_col_issue"].assert_not_awaited()


def test_only_case_citation_failure_is_non_aborting() -> None:
    assert NON_ABORTING_STEPS == {AnalysisStep.CASE_CITATION}
