"""Tests for case-analysis model routing."""

import pytest

from app.case_analyzer.config import TASK_MODELS, get_model


@pytest.mark.parametrize(
    "task",
    [
        "col_issue",
        "col_section",
        "courts_position",
        "dissenting_opinions",
        "obiter_dicta",
    ],
)
def test_complex_legal_analysis_uses_gpt_5_6_terra(task: str) -> None:
    """Complex navigation-based legal analysis uses the balanced frontier tier."""
    assert get_model(task) == "gpt-5.6-terra"


def test_lower_cost_routes_remain_on_existing_tiers() -> None:
    """Classification and generation routes preserve their existing cost profile."""
    assert TASK_MODELS["abstract"] == "gpt-5.4-mini"
    assert TASK_MODELS["relevant_facts"] == "gpt-5.4-mini"
    assert get_model("themes") == "gpt-5.4-nano"
    assert get_model("unknown") == "gpt-5.4-nano"
