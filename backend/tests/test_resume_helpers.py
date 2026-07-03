"""Tests for /analyze resume helpers."""

from app.case_analyzer.resume import (
    ANALYSIS_STEP_KEYS,
    jurisdiction_from_analyzer_data,
    load_cached_results,
)


class TestAnalysisStepKeys:
    def test_excludes_jurisdiction(self) -> None:
        assert "jurisdiction" not in ANALYSIS_STEP_KEYS

    def test_covers_all_persisted_steps(self) -> None:
        assert set(ANALYSIS_STEP_KEYS) == {
            "col_extraction",
            "theme_classification",
            "case_citation",
            "relevant_facts",
            "pil_provisions",
            "col_issue",
            "courts_position",
            "obiter_dicta",
            "dissenting_opinions",
            "abstract",
        }


class TestLoadCachedResults:
    def test_empty_analyzer_data_returns_none(self) -> None:
        assert load_cached_results({}) is None

    def test_unwraps_result_envelope(self) -> None:
        data = {"col_extraction": {"result": {"col_sections": ["x"]}}}
        assert load_cached_results(data) == {"col_extraction": {"col_sections": ["x"]}}

    def test_passes_plain_step_data_through(self) -> None:
        data = {"abstract": {"abstract": "text", "confidence": "high"}}
        assert load_cached_results(data) == {"abstract": {"abstract": "text", "confidence": "high"}}

    def test_skips_empty_and_unknown_keys(self) -> None:
        data = {"col_extraction": {}, "jurisdiction": {"precise_jurisdiction": "CH"}, "bogus": {"x": 1}}
        assert load_cached_results(data) == {}


class TestJurisdictionFromAnalyzerData:
    def test_returns_none_when_absent(self) -> None:
        assert jurisdiction_from_analyzer_data({}) is None

    def test_reconstructs_and_strips_user_confirmed(self) -> None:
        stored = {
            "legal_system_type": "Civil-law jurisdiction",
            "precise_jurisdiction": "Switzerland",
            "jurisdiction_code": "CH",
            "confidence": "high",
            "reasoning": "Swiss court.",
            "user_confirmed": True,
        }
        result = jurisdiction_from_analyzer_data({"jurisdiction": stored})
        assert result is not None
        assert result.precise_jurisdiction == "Switzerland"
        assert "user_confirmed" not in result.model_dump()

    def test_invalid_payload_returns_none(self) -> None:
        assert jurisdiction_from_analyzer_data({"jurisdiction": {"confidence": "wat"}}) is None
