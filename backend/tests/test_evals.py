"""Tests for the local analyzer eval harness: corpus parsing, scoring, cost accounting and caching."""

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.case_analyzer.jev import jev_reasoning
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


def test_to_entry_requires_full_text_and_a_curated_value() -> None:
    record = {"id": "CD-CHE-1", "originaltext": "Full text", "quote": "", "choiceoflawissue": "NA"}
    assert corpus.to_entry(record) is None
    entry = corpus.to_entry(record | {"quote": "Swiss law applies.", "pilprovisions": "Art. 116 PILA; Art. 117 PILA"})
    assert entry is not None
    assert entry["gold"]["pil_provisions"] == ["Art. 116 PILA", "Art. 117 PILA"]


def test_to_entry_falls_back_to_pdf_text() -> None:
    record = {"id": "CD-ABW-1", "originaltext": "", "jurisdictionsalpha3code": "ABW"}
    assert corpus.to_entry(record) is None
    entry = corpus.to_entry(record, pdf_text="Extracted decision text")
    assert entry is not None
    assert (entry["text"], entry["text_source"]) == ("Extracted decision text", "pdf")
    assert entry["gold"]["jurisdiction_code"] == "ABW"


def test_split_depends_only_on_the_decision_id() -> None:
    splits = {entry_id: corpus.split_of(entry_id, 0.5) for entry_id in (f"CD-{n}" for n in range(200))}
    assert set(splits.values()) == {"dev", "test"}
    assert all(corpus.split_of(entry_id, 0.5) == split for entry_id, split in splits.items())
    assert corpus.split_of("CD-1", 0.0) == "test"
    assert corpus.split_of("CD-1", 1.0) == "dev"


def test_jurisdiction_cache_covers_legal_system_sources() -> None:
    sources = run.STEPS["jurisdiction"].sources
    assert "tools/jurisdiction_detector.py" in sources
    assert "service.py" in sources
    assert run.STEPS["jurisdiction"].extra_tasks == ("legal_system",)


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

    step = run.Step("themes", ("col_excerpt", "themes"), fake_themes, ("tools/theme_classifier.py",))
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
    assert second.cases[0].attributes["answered_by"] == "openai"


@pytest.mark.asyncio
async def test_scores_are_grouped_by_answerer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)

    async def fake_themes(doc: Any, up: run.Upstream) -> StepResult[ThemeClassificationOutput]:
        by_jev = doc.text == "jev"
        reasoning = jev_reasoning("jev-1", "Party autonomy (0.97)") if by_jev else "Agent reasoning"
        themes: list[Any] = ["Party autonomy"] if by_jev else ["Public policy"]
        return StepResult(ThemeClassificationOutput(themes=themes, confidence="high", reasoning=reasoning))

    step = run.Step("themes", ("col_excerpt", "themes"), fake_themes, ("tools/theme_classifier.py",))
    entries = [{"id": f"CD-{text}", "text": text, "gold": _gold()} for text in ("jev", "agent")]
    spend = budget.Budget()
    report = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )

    summary = run.scores_by_answerer(report)
    assert summary["jev"]["cases"] == 1
    assert summary["jev"]["f1"] == 1.0
    assert summary["openai"]["f1"] == 0.0


@pytest.mark.asyncio
async def test_jev_only_themes_report_answers_by_threshold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)
    answers = {
        "confident": {"Party autonomy": 0.97, "Public policy": 0.03},
        "unsure": {"Party autonomy": 0.7, "Public policy": 0.1},
        "none": {"Party autonomy": 0.02, "Public policy": 0.01},
    }

    async def fake_probabilities(col_section: str) -> tuple[str, dict[str, float]]:
        return "jev-1", answers[col_section]

    monkeypatch.setattr(run.theme_classifier, "jev_theme_probabilities", fake_probabilities)
    step = replace(run.STEPS["themes"], run=run.JEV_ONLY_RUNS["themes"])
    entries = [{"id": f"CD-{key}", "text": "", "gold": _gold(col_excerpt=key)} for key in answers]
    spend = budget.Budget()
    report = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )

    outputs = {case.name: case.output for case in report.cases}
    assert outputs["CD-confident"]["themes"] == ["Party autonomy"]
    assert outputs["CD-none"]["jev_confidence"] == 0.0
    assert all(case.attributes["answered_by"] == "jev" for case in report.cases)
    rows = {threshold: (accepted, scored, mean) for threshold, accepted, scored, mean in run.gate_table(report, "exact")}
    assert rows[0.5] == (2, 3, 1.0)
    assert rows[0.8] == (1, 3, 1.0)


@pytest.mark.asyncio
async def test_jurisdiction_accepts_any_curated_jurisdiction() -> None:
    record = {"jurisdictions": "European Union | Netherlands", "jurisdictionsalpha3code": "EUR"}
    codes = corpus.curated_jurisdiction_codes(record)
    assert codes == ["EUR", "NLD"]
    gold = _gold(jurisdiction_code="EUR", jurisdiction_codes=codes)
    assert (await score.score("jurisdiction", {"jurisdiction_code": "NLD"}, gold))["accuracy"] == 1.0
    assert (await score.score("jurisdiction", {"jurisdiction_code": "BEL"}, gold))["accuracy"] == 0.0


def _report(cases: list[dict[str, Any]]) -> Any:
    return SimpleNamespace(cases=[SimpleNamespace(**case) for case in cases])


def test_theme_comparison_scores_both_runs_on_jevs_decisive_cases() -> None:
    gold = {"themes": ["Tacit choice"]}
    jev_report = _report(
        [
            {"name": "a", "inputs": {"gold": gold}, "output": {"probabilities": {"Tacit choice": 0.95}}},
            {"name": "b", "inputs": {"gold": gold}, "output": {"probabilities": {"Tacit choice": 0.6}}},
            {"name": "c", "inputs": {"gold": gold}, "output": {"probabilities": {"Tacit choice": 0.05}}},
            {"name": "unmatched", "inputs": {"gold": gold}, "output": {"probabilities": {"Tacit choice": 0.95}}},
        ]
    )
    openai_report = _report(
        [
            {"name": "a", "output": {"themes": ["NA"]}},
            {"name": "b", "output": {"themes": ["Tacit choice"]}},
            {"name": "c", "output": {"themes": ["Tacit choice"]}},
        ]
    )

    row = run.theme_comparison(jev_report, openai_report)["Tacit choice"]

    assert row == {
        "cases": 3,
        "decisive": 2,
        "jev_accuracy": 0.5,
        "openai_accuracy_on_decisive": 0.5,
        "openai_accuracy": 2 / 3,
    }
