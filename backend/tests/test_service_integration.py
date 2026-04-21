"""Integration tests for analyze_case_streaming event sequence and SSE contract."""

from unittest.mock import AsyncMock, patch

import pytest

from app.case_analyzer.service import analyze_case_streaming
from app.case_analyzer.tools.models import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    JurisdictionOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    StepResult,
    ThemeClassificationOutput,
)

_CIVIL_JURISDICTION = JurisdictionOutput(
    legal_system_type="Civil-law jurisdiction",
    precise_jurisdiction="Switzerland",
    jurisdiction_code="CH",
    confidence="high",
    reasoning="Swiss court.",
)

_COMMON_JURISDICTION = JurisdictionOutput(
    legal_system_type="Common-law jurisdiction",
    precise_jurisdiction="United Kingdom",
    jurisdiction_code="GB",
    confidence="high",
    reasoning="UK court.",
)


def _step(output: object, response_id: str = "resp-001") -> StepResult:
    return StepResult(output=output, response_id=response_id)


COL = ColSectionOutput(col_sections=["Art. 3 applies."], confidence="high", reasoning="ok")
THEMES = ThemeClassificationOutput(themes=["Party autonomy"], confidence="high", reasoning="ok")
CITATION = CaseCitationOutput(case_citation="BGE 123 III 456", confidence="high", reasoning="ok")
FACTS = RelevantFactsOutput(relevant_facts="The parties signed a contract.", confidence="high", reasoning="ok")
PROVISIONS = PILProvisionsOutput(pil_provisions=["Art. 3 Rome I"], confidence="high", reasoning="ok")
ISSUE = ColIssueOutput(col_issue="Which law governs?", confidence="high", reasoning="ok")
POSITION = CourtsPositionOutput(courts_position="Swiss law applies.", confidence="high", reasoning="ok")
OBITER = ObiterDictaOutput(obiter_dicta="The court noted in passing...", confidence="high", reasoning="ok")
DISSENT = DissentingOpinionsOutput(dissenting_opinions="Judge X disagreed.", confidence="high", reasoning="ok")
ABSTRACT = AbstractOutput(abstract="This case concerns CoL.", confidence="high", reasoning="ok")

_SERVICE = "app.case_analyzer.service"

_CIVIL_PATCHES: dict[str, AsyncMock] = {
    "extract_col_section": AsyncMock(return_value=_step(COL)),
    "classify_themes": AsyncMock(return_value=_step(THEMES)),
    "extract_case_citation": AsyncMock(return_value=_step(CITATION)),
    "extract_relevant_facts": AsyncMock(return_value=_step(FACTS)),
    "extract_pil_provisions": AsyncMock(return_value=_step(PROVISIONS)),
    "extract_col_issue": AsyncMock(return_value=_step(ISSUE)),
    "extract_courts_position": AsyncMock(return_value=_step(POSITION)),
    "extract_abstract": AsyncMock(return_value=_step(ABSTRACT)),
}

_COMMON_PATCHES: dict[str, AsyncMock] = {
    **_CIVIL_PATCHES,
    "extract_obiter_dicta": AsyncMock(return_value=_step(OBITER)),
    "extract_dissenting_opinions": AsyncMock(return_value=_step(DISSENT)),
}


async def _collect(jurisdiction: JurisdictionOutput, cached: dict | None = None, draft_id: int = 0) -> list[dict]:
    events = []
    async for event in analyze_case_streaming("decision text", jurisdiction, cached, draft_id=draft_id):
        events.append(event)
    return events


def _by_step(events: list[dict]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for e in events:
        result.setdefault(e["step"], []).append(e["status"])
    return result


class TestCivilLawStream:
    @pytest.mark.asyncio
    async def test_all_expected_steps_present(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        by_step = _by_step(events)

        for step in (
            "col_extraction",
            "theme_classification",
            "case_citation",
            "relevant_facts",
            "pil_provisions",
            "col_issue",
            "courts_position",
            "abstract",
        ):
            assert step in by_step, f"missing step: {step}"
            assert "completed" in by_step[step]

    @pytest.mark.asyncio
    async def test_no_common_law_steps(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        by_step = _by_step(events)
        assert "obiter_dicta" not in by_step
        assert "dissenting_opinions" not in by_step

    @pytest.mark.asyncio
    async def test_consistency_check_removed(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        assert all(e["step"] != "consistency_check" for e in events)

    @pytest.mark.asyncio
    async def test_final_event_is_analysis_complete(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        last = events[-1]
        assert last["step"] == "analysis_complete"
        assert last["status"] == "completed"

    @pytest.mark.asyncio
    async def test_each_step_has_in_progress_then_completed(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        by_step = _by_step(events)
        for step in ("col_extraction", "col_issue", "courts_position", "abstract"):
            statuses = by_step[step]
            assert statuses[0] == "in_progress"
            assert "completed" in statuses

    @pytest.mark.asyncio
    async def test_completed_events_have_data_field(self) -> None:
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        for e in events:
            if e["status"] == "completed" and e["step"] != "analysis_complete":
                assert "data" in e, f"missing data in {e['step']} completed event"


class TestCommonLawStream:
    @pytest.mark.asyncio
    async def test_includes_obiter_and_dissent(self) -> None:
        with patch.multiple(_SERVICE, **_COMMON_PATCHES):
            events = await _collect(_COMMON_JURISDICTION, draft_id=2)
        by_step = _by_step(events)
        assert "obiter_dicta" in by_step
        assert "dissenting_opinions" in by_step
        assert "completed" in by_step["obiter_dicta"]
        assert "completed" in by_step["dissenting_opinions"]


class TestResumeFromCache:
    @pytest.mark.asyncio
    async def test_cached_col_skips_extraction(self) -> None:
        cached = {"col_extraction": {"col_sections": ["Art. 3 applies."], "confidence": "high", "reasoning": "ok"}}
        col_mock = AsyncMock(return_value=_step(COL))
        patches_without_col = {k: v for k, v in _CIVIL_PATCHES.items() if "col_section" not in k}
        patches_without_col["extract_col_section"] = col_mock

        with patch.multiple(_SERVICE, **patches_without_col):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        col_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_step_emits_completed_immediately(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
        }
        with patch.multiple(_SERVICE, **_CIVIL_PATCHES):
            events = await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        col_events = [e for e in events if e["step"] == "col_extraction"]
        assert len(col_events) == 1
        assert col_events[0]["status"] == "completed"


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_col_extraction_failure_stops_stream(self) -> None:
        failing_patches = dict(_CIVIL_PATCHES)
        failing_patches["extract_col_section"] = AsyncMock(side_effect=RuntimeError("API timeout"))
        with patch.multiple(_SERVICE, **failing_patches):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)

        error_events = [e for e in events if e["status"] == "error"]
        assert len(error_events) == 1
        assert error_events[0]["step"] == "col_extraction"
        assert "analysis_complete" not in [e["step"] for e in events]
