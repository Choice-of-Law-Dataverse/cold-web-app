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
CITATION = CaseCitationOutput(
    case_citation="BGE 123 III 456",
    source_text="BGE 123 III 456",
    source_location="document beginning",
    identifier_type="reporter citation",
    confidence="high",
    reasoning="ok",
)
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


async def _collect(
    jurisdiction: JurisdictionOutput,
    cached: dict | None = None,
    draft_id: int = 0,
    file_name: str | None = None,
) -> list[dict]:
    events = []
    async for event in analyze_case_streaming(
        "decision text",
        cached,
        draft_id=draft_id,
        jurisdiction_override=jurisdiction,
        file_name=file_name,
    ):
        events.append(event)
    return events


def _by_step(events: list[dict]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for e in events:
        result.setdefault(e["step"], []).append(e["status"])
    return result


class TestCivilLawStream:
    @pytest.mark.asyncio
    async def test_original_filename_reaches_citation_extractor(self) -> None:
        citation_mock = AsyncMock(return_value=_step(CITATION))
        patches = {**_CIVIL_PATCHES, "extract_case_citation": citation_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, draft_id=1, file_name="decision-2026-XYZ.pdf")

        citation_call = citation_mock.await_args
        assert citation_call is not None
        citation_context = citation_call.args[0]
        assert citation_context.file_name == "decision-2026-XYZ.pdf"

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

    @pytest.mark.asyncio
    async def test_legacy_negative_citation_without_evidence_is_recomputed(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
            "case_citation": {"case_citation": "NA", "confidence": "low", "reasoning": "Not found"},
        }
        citation_mock = AsyncMock(return_value=_step(CITATION))
        patches = {**_CIVIL_PATCHES, "extract_case_citation": citation_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        citation_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_inspected_negative_citation_from_older_policy_is_recomputed(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
            "case_citation": {
                "case_citation": "NA",
                "confidence": "high",
                "reasoning": "Not found after searching",
                "_evidence": {"navigation_tools": ["search"]},
            },
        }
        citation_mock = AsyncMock(return_value=_step(CITATION))
        patches = {**_CIVIL_PATCHES, "extract_case_citation": citation_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        citation_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_inspected_negative_citation_is_restored_from_cache(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
            "case_citation": {
                "case_citation": "NA",
                "source_text": None,
                "source_location": None,
                "identifier_type": None,
                "confidence": "low",
                "reasoning": "Not found",
                "_evidence": {"navigation_tools": ["search"], "policy_version": 7},
            },
        }
        citation_mock = AsyncMock(return_value=_step(CITATION))
        patches = {**_CIVIL_PATCHES, "extract_case_citation": citation_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        citation_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_non_citation_step_from_context_chaining_policy_is_recomputed(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
            "theme_classification": {
                "themes": ["Mandatory rules"],
                "confidence": "high",
                "reasoning": "Old chained-context result",
                "_evidence": {"navigation_tools": [], "policy_version": 5},
            },
        }
        theme_mock = AsyncMock(return_value=_step(THEMES))
        patches = {**_CIVIL_PATCHES, "classify_themes": theme_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        theme_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_inspected_empty_provisions_are_restored_from_cache(self) -> None:
        cached = {
            "col_extraction": {"col_sections": ["Art. 3."], "confidence": "high", "reasoning": "ok"},
            "pil_provisions": {
                "pil_provisions": [],
                "confidence": "medium",
                "reasoning": "No provisions found",
                "_evidence": {"navigation_tools": ["search"]},
            },
        }
        provisions_mock = AsyncMock(return_value=_step(PROVISIONS))
        patches = {**_CIVIL_PATCHES, "extract_pil_provisions": provisions_mock}

        with patch.multiple(_SERVICE, **patches):
            await _collect(_CIVIL_JURISDICTION, cached=cached, draft_id=1)

        provisions_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_fresh_step_includes_persistable_tool_evidence(self) -> None:
        citation_step = StepResult(output=CITATION, response_id="resp", tool_names=("read_head", "search"))
        citation_mock = AsyncMock(return_value=citation_step)
        patches = {**_CIVIL_PATCHES, "extract_case_citation": citation_mock}

        with patch.multiple(_SERVICE, **patches):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)

        citation_event = next(event for event in events if event["step"] == "case_citation" and event["status"] == "completed")
        assert citation_event["data"]["_evidence"] == {
            "navigation_tools": ["read_head", "search"],
            "policy_version": 7,
        }
        assert citation_event["data"]["case_citation"] == CITATION.case_citation
        assert citation_event["data"]["source_text"] == CITATION.source_text
        assert citation_event["data"]["source_location"] == CITATION.source_location
        assert citation_event["data"]["identifier_type"] == CITATION.identifier_type
        citation_mock.assert_awaited_once()
        citation_call = citation_mock.await_args
        assert citation_call is not None
        assert "previous_response_id" not in citation_call.kwargs


async def _collect_auto_detect(cached: dict | None = None, draft_id: int = 0) -> list[dict]:
    events = []
    async for event in analyze_case_streaming("decision text", cached, draft_id=draft_id):
        events.append(event)
    return events


class TestAutoDetectPath:
    @pytest.mark.asyncio
    async def test_auto_detect_emits_jurisdiction_events(self) -> None:
        patches = {**_CIVIL_PATCHES, "detect_jurisdiction": AsyncMock(return_value=_CIVIL_JURISDICTION)}
        with patch.multiple(_SERVICE, **patches):
            events = await _collect_auto_detect(draft_id=1)
        by_step = _by_step(events)
        assert "jurisdiction_detection" in by_step
        assert by_step["jurisdiction_detection"] == ["in_progress", "completed"]

    @pytest.mark.asyncio
    async def test_auto_detect_includes_jurisdiction_data(self) -> None:
        patches = {**_CIVIL_PATCHES, "detect_jurisdiction": AsyncMock(return_value=_CIVIL_JURISDICTION)}
        with patch.multiple(_SERVICE, **patches):
            events = await _collect_auto_detect(draft_id=1)
        jurisdiction_completed = [e for e in events if e["step"] == "jurisdiction_detection" and e["status"] == "completed"]
        assert len(jurisdiction_completed) == 1
        assert jurisdiction_completed[0]["data"]["precise_jurisdiction"] == "Switzerland"

    @pytest.mark.asyncio
    async def test_auto_detect_failure_stops_stream(self) -> None:
        patches = {**_CIVIL_PATCHES, "detect_jurisdiction": AsyncMock(side_effect=RuntimeError("detection failed"))}
        with patch.multiple(_SERVICE, **patches):
            events = await _collect_auto_detect(draft_id=1)
        by_step = _by_step(events)
        assert "error" in by_step["jurisdiction_detection"]
        assert "analysis_complete" not in by_step

    @pytest.mark.asyncio
    async def test_auto_detect_failure_skips_downstream_steps(self) -> None:
        patches = {
            **_CIVIL_PATCHES,
            "detect_jurisdiction": AsyncMock(side_effect=RuntimeError("detection failed")),
        }
        with patch.multiple(_SERVICE, **patches):
            events = await _collect_auto_detect(draft_id=1)
        by_step = _by_step(events)
        for step in ("theme_classification", "case_citation", "relevant_facts", "pil_provisions"):
            assert step not in by_step, f"downstream step {step} should not appear after jurisdiction failure"


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


class TestEmptyColSections:
    @pytest.mark.asyncio
    async def test_empty_col_sections_fail_the_stream(self) -> None:
        empty = ColSectionOutput(col_sections=[], confidence="low", reasoning="nothing found")
        patches = dict(_CIVIL_PATCHES)
        patches["extract_col_section"] = AsyncMock(return_value=_step(empty))
        with patch.multiple(_SERVICE, **patches):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        by_step = _by_step(events)
        assert "error" in by_step["col_extraction"]
        assert "theme_classification" not in by_step
        assert "analysis_complete" not in by_step

    @pytest.mark.asyncio
    async def test_whitespace_only_col_sections_fail_the_stream(self) -> None:
        blank = ColSectionOutput(col_sections=["   ", "\n"], confidence="low", reasoning="noise")
        patches = dict(_CIVIL_PATCHES)
        patches["extract_col_section"] = AsyncMock(return_value=_step(blank))
        with patch.multiple(_SERVICE, **patches):
            events = await _collect(_CIVIL_JURISDICTION, draft_id=1)
        by_step = _by_step(events)
        assert "error" in by_step["col_extraction"]
        assert "analysis_complete" not in by_step
