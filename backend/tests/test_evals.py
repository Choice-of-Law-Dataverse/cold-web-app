"""Tests for the local analyzer eval harness: corpus parsing, scoring, cost accounting and caching."""

import json
from pathlib import Path
from typing import Any

import pytest

from app.case_analyzer.tools.models import StepResult, ThemeClassificationOutput
from evals import budget, corpus, run, score


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


def test_budget_stops_new_calls_at_the_limit() -> None:
    spend = budget.Budget(max_cost=1.0, spent=0.99)
    spend.check()
    spend.spent = 1.0
    with pytest.raises(budget.BudgetExceeded):
        spend.check()


@pytest.mark.asyncio
async def test_experiment_caches_outputs_and_replays_their_cost(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)
    calls: list[str] = []

    async def fake_themes(doc: Any, up: run.Upstream) -> StepResult[ThemeClassificationOutput]:
        calls.append(up.legal_system)
        return StepResult(ThemeClassificationOutput(themes=["Party autonomy"], confidence="high", reasoning="ok"))

    step = run.Step("themes", ("col_excerpt", "themes"), fake_themes, "theme_classifier")
    entries = [
        {"id": "CD-CHE-1", "text": "Decision text", "gold": _gold()},
        {"id": "CD-CHE-2", "text": "", "gold": _gold(themes=[])},
    ]
    spend = budget.Budget()

    first = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )
    cache_file = next(tmp_path.iterdir())
    cache_file.write_text(json.dumps(json.loads(cache_file.read_text()) | {"metrics": {"cost": 0.25}}))
    second = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )

    assert calls == ["Civil-law jurisdiction"]
    assert [case.name for case in first.cases] == ["CD-CHE-1"]
    assert first.cases[0].scores["f1"].value == 1.0
    assert second.cases[0].attributes["cached"] is True
    assert run.total_cost(second) == 0.25
