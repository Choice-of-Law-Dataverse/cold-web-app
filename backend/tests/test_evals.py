"""Tests for the local analyzer eval harness: corpus parsing, scoring, cost accounting and caching."""

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.case_analyzer.jev import NoulAnswer, SystemOneResponse, Usage, jev_reasoning
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

    step = replace(run.STEPS["themes"], run=fake_themes)
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

    step = replace(run.STEPS["themes"], run=fake_themes)
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
            {"name": "a", "expected_output": gold, "output": {"probabilities": {"Tacit choice": 0.95}}},
            {"name": "b", "expected_output": gold, "output": {"probabilities": {"Tacit choice": 0.6}}},
            {"name": "c", "expected_output": gold, "output": {"probabilities": {"Tacit choice": 0.05}}},
            {"name": "unmatched", "expected_output": gold, "output": {"probabilities": {"Tacit choice": 0.95}}},
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


@pytest.mark.parametrize("name", list(run.STEPS))
def test_task_inputs_never_contain_the_scored_answer_or_the_decision_id(name: str) -> None:
    step = run.STEPS[name]
    entry = {"id": "CD-CHE-1", "text": "Decision text", "text_source": "pdf", "gold": _gold(jurisdiction_codes=["CHE"])}
    inputs = run.case_inputs(step, entry)

    assert set(inputs) == {"text", "upstream"}
    assert set(inputs["upstream"]).isdisjoint(step.target)
    assert "CD-CHE-1" not in json.dumps(inputs)
    if name == "jurisdiction":
        assert inputs["upstream"] == {}
        assert "CHE" not in json.dumps(inputs)


@pytest.mark.asyncio
async def test_a_step_cannot_read_a_curated_value_it_does_not_declare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)

    async def peeking(_doc: Any, up: run.Upstream) -> dict[str, Any]:
        return {"themes": up.themes.themes}

    step = replace(run.STEPS["themes"], run=peeking)
    entries = [{"id": "CD-CHE-1", "text": "Decision text", "gold": _gold()}]
    spend = budget.Budget()
    report = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )

    assert not report.cases
    assert "KeyError" in report.failures[0].error_message


def _agreeing_judge(calls: list[str]) -> Any:
    async def ask(step: str, state: Any, questions: dict) -> SystemOneResponse:
        calls.append(step)
        return SystemOneResponse(model="jev-1", answers={"agrees": NoulAnswer(type="noul", noul=0.9)}, usage=Usage(cost=0.01))

    return ask


@pytest.mark.asyncio
async def test_judge_cost_is_tracked_apart_and_the_budget_stops_judging_cached_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)
    judged: list[str] = []
    monkeypatch.setattr(score, "ask_jev", _agreeing_judge(judged))

    async def fake_issue(_doc: Any, _up: run.Upstream) -> dict[str, Any]:
        return {"col_issue": "Which law governs the contract?"}

    step = replace(run.STEPS["col_issue"], run=fake_issue)
    entries = [{"id": "CD-CHE-1", "text": "Decision text", "gold": _gold(col_issue="Which law governs?")}]
    spend = budget.Budget()
    first = await run.build_dataset("col_issue", step, entries, spend).evaluate(
        run.make_task("col_issue", step, spend), progress=False
    )
    assert first.cases[0].scores["agreement"].value == 0.9
    assert (spend.spent, spend.judge_spent, spend.total) == (0.0, 0.01, 0.01)

    capped = budget.Budget(max_cost=0.5, judge_spent=0.5)
    second = await run.build_dataset("col_issue", step, entries, capped).evaluate(
        run.make_task("col_issue", step, capped), progress=False
    )

    assert second.cases[0].attributes["cached"] is True
    assert "agreement" not in second.cases[0].scores
    assert run.budget_stopped(second) == (0, 1)
    assert judged == ["eval_judge"]


def test_budget_counts_the_judge_towards_the_limit() -> None:
    spend = budget.Budget(max_cost=1.0, spent=0.6)
    spend.add_judge_cost(0.3)
    spend.check()
    spend.add_judge_cost(None)
    spend.add_judge_cost(0.1)
    assert spend.unpriced_calls == 1
    with pytest.raises(budget.BudgetExceeded):
        spend.check()


@pytest.mark.asyncio
async def test_undecided_legal_family_is_detected_once_and_cached_with_the_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(run, "CACHE_DIR", tmp_path)
    detections: list[tuple[str, str]] = []

    async def fake_detect(jurisdiction: str, text: str, fallback: str | None = None) -> str:
        detections.append((jurisdiction, text))
        return "Common-law jurisdiction"

    monkeypatch.setattr(run, "detect_legal_system_type", fake_detect)
    systems: list[str] = []

    async def fake_themes(_doc: Any, up: run.Upstream) -> StepResult[ThemeClassificationOutput]:
        systems.append(up.legal_system)
        return StepResult(ThemeClassificationOutput(themes=["Party autonomy"], confidence="high", reasoning="ok"))

    step = replace(run.STEPS["themes"], run=fake_themes)
    entries = [
        {"id": "CD-ZAF-1", "text": "South African decision", "gold": _gold(jurisdiction="South Africa")},
        {"id": "CD-CHE-1", "text": "Swiss decision", "gold": _gold()},
    ]
    spend = budget.Budget()
    first = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )
    second = await run.build_dataset("themes", step, entries, spend).evaluate(
        run.make_task("themes", step, spend), progress=False
    )

    assert detections == [("South Africa", "South African decision")]
    assert sorted(systems) == ["Civil-law jurisdiction", "Common-law jurisdiction"]
    replayed = {case.name: case.attributes for case in second.cases}
    assert replayed["CD-ZAF-1"]["cached"] is True
    assert (replayed["CD-ZAF-1"]["legal_system"], replayed["CD-ZAF-1"]["legal_system_detected"]) == (
        "Common-law jurisdiction",
        True,
    )
    assert replayed["CD-CHE-1"]["legal_system_detected"] is False
    assert {case.name: case.attributes["legal_system"] for case in first.cases}["CD-CHE-1"] == "Civil-law jurisdiction"


def test_only_an_undecided_legal_family_keys_the_cache_on_the_detector() -> None:
    step = run.STEPS["themes"]
    swiss = run.case_inputs(step, {"text": "t", "gold": _gold()})
    south_african = run.case_inputs(step, {"text": "t", "gold": _gold(jurisdiction="South Africa")})
    assert run._legal_system_dependency(step, swiss) is None
    assert run._legal_system_dependency(step, south_african) is not None
    assert run._legal_system_dependency(run.STEPS["col_section"], south_african) is None


def test_col_section_cache_covers_the_retrieval_planner_and_the_chunk_size() -> None:
    assert "col_retrieval" in run.STEPS["col_section"].extra_tasks
    assert "tools/semantic_index.py" in run.SHARED_SOURCES


def test_short_extract_of_a_long_excerpt_cannot_get_full_recall() -> None:
    excerpt = "The parties validly chose Swiss law, so Swiss law governs the whole of the sales contract."
    assert score.excerpt_recall(["Swiss law"], excerpt) == pytest.approx(len("swiss law") / len(score.normalize(excerpt)))
    assert score.excerpt_recall(["Background.", excerpt], excerpt) == pytest.approx(1.0)
    assert score.excerpt_recall([], excerpt) == 0.0


@pytest.mark.parametrize(
    ("identifier", "reference", "expected"),
    [
        ("12", "312", 0.0),
        ("1/23", "12/3", 0.0),
        ("4A_123/2020", "BGer 4A_123/2020", 1.0),
        ("2015 NSWSC 468", "[2015] NSWSC 468", 1.0),
        ("", "BGer 4A_123/2020", 0.0),
    ],
)
def test_identifier_match_compares_whole_numbers(identifier: str, reference: str, expected: float) -> None:
    assert score.identifier_match(identifier, reference) == expected


def test_text_is_paired_with_the_excerpt_in_its_language() -> None:
    record = {"id": "CD-PER-1", "quote": "Se aplica la ley peruana.", "englishtranslation": "Peruvian law applies here."}
    assert corpus.text_and_excerpt(record) == ("englishtranslation", "Peruvian law applies here.", "Se aplica la ley peruana.")
    assert corpus.text_and_excerpt(record, pdf_text="Texto original") == (
        "pdf",
        "Texto original",
        "Se aplica la ley peruana.",
    )
    translated = record | {"translatedexcerpt": "Peruvian law applies."}
    assert corpus.text_and_excerpt(translated, pdf_text="Texto original") == (
        "englishtranslation",
        "Peruvian law applies here.",
        "Peruvian law applies.",
    )
    original = translated | {"originaltext": "Texto completo"}
    assert corpus.text_and_excerpt(original, pdf_text="Texto original") == (
        "originaltext",
        "Texto completo",
        "Se aplica la ley peruana.",
    )
    assert corpus.text_and_excerpt({"id": "CD-X-1"}) == (None, "", "")
