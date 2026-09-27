"""Tests for the local analyzer eval harness: corpus parsing, scoring, cost accounting and caching."""

from pathlib import Path
from typing import Any

import pytest

from app.case_analyzer.tools.models import StepResult, ThemeClassificationOutput
from evals import corpus, run, score, usage


def _gold(**overrides: Any) -> dict[str, Any]:
    return {
        "jurisdiction_code": "CHE",
        "jurisdiction": "Switzerland",
        "col_excerpt": "The parties chose Swiss law under Art. 116 PILA.",
        "themes": ["Party autonomy"],
        "case_citation": "BGE 140 III 473",
        "pil_provisions": ["Art. 116 PILA"],
        "relevant_facts": "",
        "col_issue": "",
        "courts_position": "",
        "abstract": "",
    } | overrides


def test_curated_themes_split_on_pipes_and_map_aliases() -> None:
    value = "Freedom of choice | Party autonomy | Overriding mandatory rules | Codification"
    assert corpus.curated_themes(value) == ["Freedom of Choice", "Mandatory rules", "Party autonomy"]


def test_to_entry_requires_full_text_and_curated_col_analysis() -> None:
    record = {"id": "CD-CHE-1", "originaltext": "Full text", "quote": "", "choiceoflawissue": "NA"}
    assert corpus.to_entry(record) is None
    entry = corpus.to_entry(record | {"quote": "Swiss law applies.", "pilprovisions": "Art. 116 PILA; Art. 117 PILA"})
    assert entry is not None
    assert entry["gold"]["pil_provisions"] == ["Art. 116 PILA", "Art. 117 PILA"]


def test_set_scores_match_fuzzily() -> None:
    result = score.set_scores(["Article 116 PILA", "Art. 18 PILA"], ["Art. 116 PILA"])
    assert result["recall"] == 1.0
    assert result["precision"] == 0.5


@pytest.mark.asyncio
async def test_col_section_scores_excerpt_recall() -> None:
    output = {"col_sections": ["Background.", "The parties chose Swiss law under Art. 116 PILA."]}
    scores = await score.score("col_section", output, _gold())
    assert scores["excerpt_recall"] == 1.0


def test_usage_tracker_prices_dated_snapshots_and_cached_input() -> None:
    tracker = usage.UsageTracker({"gpt-5.4-nano": {"input": 1.0, "cached_input": 0.1, "output": 4.0}})
    row = usage.StepUsage()
    token = usage.current_row.set(row)
    step_token = usage.current_step.set("themes")
    try:
        tracker.record(
            "gpt-5.4-nano-2026-08-01",
            {"input_tokens": 1_000_000, "input_tokens_details": {"cached_tokens": 500_000}, "output_tokens": 250_000},
        )
    finally:
        usage.current_row.reset(token)
        usage.current_step.reset(step_token)
    assert row.cost == pytest.approx(0.5 + 0.05 + 1.0)
    assert tracker.steps["themes"].cost == pytest.approx(row.cost)


def test_usage_tracker_flags_unpriced_models_and_enforces_budget() -> None:
    tracker = usage.UsageTracker({"gpt-5.4-nano": {"input": 100.0}}, max_cost=0.5)
    token = usage.current_step.set("pil_provisions")
    try:
        tracker.record("gpt-9", {"input_tokens": 10})
        tracker.record("gpt-5.4-nano", {"input_tokens": 10_000})
    finally:
        usage.current_step.reset(token)
    assert "gpt-9" in tracker.steps["pil_provisions"].unpriced_models
    with pytest.raises(usage.BudgetExceeded):
        tracker.check_budget()


@pytest.mark.asyncio
async def test_run_one_caches_step_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)
    calls: list[str] = []

    async def fake_themes(doc: Any, up: run.Upstream) -> StepResult[ThemeClassificationOutput]:
        calls.append(up.legal_system)
        return StepResult(ThemeClassificationOutput(themes=["Party autonomy"], confidence="high", reasoning="ok"))

    step = run.Step("themes", ("col_excerpt", "themes"), fake_themes, "theme_classifier")
    entry = {"id": "CD-CHE-1", "text": "Decision text", "gold": _gold()}
    tracker = usage.UsageTracker({})

    first = await run.run_one("themes", step, entry, tracker)
    second = await run.run_one("themes", step, entry, tracker)

    assert calls == ["Civil-law jurisdiction"]
    assert first["scores"]["f1"] == 1.0
    assert second["cached"] is True
    assert second["scores"] == first["scores"]
