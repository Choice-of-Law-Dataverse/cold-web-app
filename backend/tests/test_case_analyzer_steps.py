"""Tests for the case analysis step identity module."""

import pytest

from app.case_analyzer.resume import ANALYSIS_STEP_KEYS
from app.case_analyzer.steps import CACHEABLE_STEPS, AnalysisStep, persisted_key


class TestPersistedKey:
    def test_maps_jurisdiction_detection_to_jurisdiction(self) -> None:
        assert persisted_key("jurisdiction_detection") == "jurisdiction"
        assert persisted_key(AnalysisStep.JURISDICTION_DETECTION) == "jurisdiction"

    @pytest.mark.parametrize("step", [step for step in AnalysisStep if step is not AnalysisStep.JURISDICTION_DETECTION])
    def test_is_identity_for_every_other_step(self, step: AnalysisStep) -> None:
        assert persisted_key(step) == step.value
        assert persisted_key(step.value) == step.value

    def test_returns_a_plain_string(self) -> None:
        assert type(persisted_key(AnalysisStep.ABSTRACT)) is str

    def test_passes_unknown_names_through(self) -> None:
        assert persisted_key("heartbeat") == "heartbeat"


class TestCacheableSteps:
    def test_order_and_contents_are_stable(self) -> None:
        assert [str(step) for step in CACHEABLE_STEPS] == [
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
        ]

    def test_resume_exposes_the_same_keys_as_a_list(self) -> None:
        assert isinstance(ANALYSIS_STEP_KEYS, list)
        assert ANALYSIS_STEP_KEYS == list(CACHEABLE_STEPS)

    def test_wire_values_are_the_current_sse_names(self) -> None:
        assert {step.value for step in AnalysisStep} == {
            "jurisdiction_detection",
            "col_extraction",
            "theme_classification",
            "case_citation",
            "relevant_facts",
            "pil_provisions",
            "parallel_tasks",
            "col_issue",
            "courts_position",
            "obiter_dicta",
            "dissenting_opinions",
            "abstract",
            "analysis_complete",
        }
