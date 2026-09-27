"""Run analyzer steps over the eval corpus as pydantic-evals experiments.

Each step is run in isolation: its upstream inputs (CoL section, themes, CoL issue, ...) are
the curated values, so testing one step never pays for the steps before it, and a weak
upstream step cannot drag a downstream score down. Step outputs are cached on disk by step,
model, analyzer source and input, so re-runs only pay for what changed. Cost per case comes
from Logfire's pricing of each model call; cached cases report the cost recorded when they ran.

    uv run python -m evals.run --split dev --steps themes,col_issue --name baseline --max-cost 2
    uv run python -m evals.run --split dev --steps themes --name mini \\
        --models '{"themes": "gpt-5.4-mini"}' --baseline baseline
    uv run python -m evals.run --split dev --steps jurisdiction,themes --jev-only --name jev
"""

import argparse
import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_evals import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput
from pydantic_evals.reporting import EvaluationReport, EvaluationReportAdapter

from app.case_analyzer.config import TASK_MODELS, get_model
from app.case_analyzer.jev import answered_by_jev, jev_reasoning
from app.case_analyzer.service import detect_jurisdiction
from app.case_analyzer.tools import (
    classify_themes,
    col_extractor,
    extract_abstract,
    extract_case_citation,
    extract_col_issue,
    extract_col_section,
    extract_courts_position,
    extract_pil_provisions,
    extract_relevant_facts,
    jurisdiction_classifier,
    jurisdiction_detector,
    theme_classifier,
)
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.hybrid_retrieval import retrieve_choice_of_law_candidates
from app.case_analyzer.tools.jurisdiction_detector import detect_legal_system_by_jurisdiction
from app.case_analyzer.tools.models import (
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    StepResult,
    ThemeClassificationOutput,
)
from app.config import config

from . import corpus
from .budget import Budget, configure_logfire
from .score import excerpt_recall, score

JEV_ENABLED = True
JEV_ONLY = False
GATE_THRESHOLDS = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95)
PRUNING_THRESHOLDS = (0.1, 0.3, 0.5, 0.7, 0.9)
RUNS_DIR = corpus.EVAL_DIR / "runs"
CACHE_DIR = corpus.EVAL_DIR / "cache"
ANALYZER_DIR = Path(__file__).resolve().parent.parent / "app" / "case_analyzer"
METRICS = ("cost", "input_tokens", "output_tokens", "requests")


class Upstream:
    """Curated values in the shapes the analyzer steps take as inputs."""

    def __init__(self, gold: dict[str, Any]) -> None:
        self.gold = gold
        self.jurisdiction = gold["jurisdiction"] or None
        curated = [detect_legal_system_by_jurisdiction(name) for name in corpus.split_list(gold["jurisdiction"])]
        self.legal_system = next((system for system in curated if system), "Civil-law jurisdiction")
        self.col = ColSectionOutput(col_sections=[gold["col_excerpt"]], confidence="high", reasoning="Curated")
        self.themes = ThemeClassificationOutput(themes=gold["themes"] or ["NA"], confidence="high", reasoning="Curated")
        self.facts = RelevantFactsOutput(relevant_facts=gold["relevant_facts"], confidence="high", reasoning="Curated")
        self.provisions = PILProvisionsOutput(pil_provisions=gold["pil_provisions"], confidence="high", reasoning="Curated")
        self.issue = ColIssueOutput(col_issue=gold["col_issue"], confidence="high", reasoning="Curated")
        self.position = CourtsPositionOutput(courts_position=gold["courts_position"], confidence="high", reasoning="Curated")


@dataclass(frozen=True)
class Step:
    """An analyzer step; sources (relative to app/case_analyzer) and tasks key its cache."""

    task: str
    requires: tuple[str, ...]
    run: Callable[[DocumentContext, Upstream], Awaitable[Any]]
    sources: tuple[str, ...]
    extra_tasks: tuple[str, ...] = ()


async def _jurisdiction(doc: DocumentContext, _up: Upstream) -> Any:
    return await detect_jurisdiction(doc.text)


STEPS: dict[str, Step] = {
    "jurisdiction": Step(
        "jurisdiction_classification",
        ("jurisdiction_code",),
        _jurisdiction,
        ("service.py", "tools/jurisdiction_classifier.py", "tools/jurisdiction_detector.py"),
        ("legal_system",),
    ),
    "col_section": Step(
        "col_section",
        ("col_excerpt",),
        lambda doc, up: extract_col_section(doc),
        ("tools/col_extractor.py", "tools/hybrid_retrieval.py"),
    ),
    "themes": Step(
        "themes",
        ("col_excerpt", "themes"),
        lambda doc, up: classify_themes(doc, up.gold["col_excerpt"], up.legal_system, up.jurisdiction),
        ("tools/theme_classifier.py",),
    ),
    "case_citation": Step(
        "case_citation",
        ("case_citation",),
        lambda doc, up: extract_case_citation(doc, up.legal_system, up.jurisdiction or ""),
        ("tools/case_citation_extractor.py",),
    ),
    "pil_provisions": Step(
        "pil_provisions",
        ("col_excerpt", "pil_provisions"),
        lambda doc, up: extract_pil_provisions(doc, up.col, up.legal_system, up.jurisdiction),
        ("tools/pil_provisions_extractor.py",),
    ),
    "relevant_facts": Step(
        "relevant_facts",
        ("col_excerpt", "relevant_facts"),
        lambda doc, up: extract_relevant_facts(doc, up.col, up.legal_system, up.jurisdiction),
        ("tools/relevant_facts_extractor.py",),
    ),
    "col_issue": Step(
        "col_issue",
        ("col_excerpt", "themes", "col_issue"),
        lambda doc, up: extract_col_issue(doc, up.col, up.legal_system, up.jurisdiction, up.themes),
        ("tools/col_issue_extractor.py",),
    ),
    "courts_position": Step(
        "courts_position",
        ("col_excerpt", "themes", "col_issue", "courts_position"),
        lambda doc, up: extract_courts_position(doc, up.col, up.legal_system, up.jurisdiction, up.themes, up.issue),
        ("tools/courts_position_extractor.py",),
    ),
    "abstract": Step(
        "abstract",
        ("themes", "relevant_facts", "pil_provisions", "col_issue", "courts_position", "abstract"),
        lambda doc, up: extract_abstract(
            doc, up.legal_system, up.jurisdiction, up.themes, up.facts, up.provisions, up.issue, up.position
        ),
        ("tools/abstract_generator.py",),
    ),
}


async def _jev_jurisdiction(doc: DocumentContext, _up: Upstream) -> dict[str, Any]:
    result = await jurisdiction_classifier.jev_jurisdiction(doc.text)
    if result is None:
        raise RuntimeError("Jev gave no jurisdiction answer; see the logged request error")
    model, answer = result
    return {
        "jurisdiction_code": jurisdiction_classifier.jurisdiction_codes().get(answer.choice, ""),
        "jev_confidence": answer.confidence,
        "reasoning": jev_reasoning(model, f"{answer.choice} ({answer.confidence:.2f})"),
    }


async def _jev_themes(_doc: DocumentContext, up: Upstream) -> dict[str, Any]:
    """Jev's themes; confidence 0 when no theme applies, since the analyzer never accepts that answer from Jev."""
    result = await theme_classifier.jev_theme_probabilities(up.gold["col_excerpt"])
    if result is None:
        raise RuntimeError("Jev gave no theme answers; see the logged request error")
    model, probabilities = result
    selected = [theme for theme, p in probabilities.items() if p >= 0.5]
    decisiveness = min(max(p, 1 - p) for p in probabilities.values())
    return {
        "themes": selected,
        "probabilities": probabilities,
        "jev_confidence": decisiveness if selected else 0.0,
        "reasoning": jev_reasoning(model, ", ".join(f"{theme} ({p:.2f})" for theme, p in probabilities.items())),
    }


async def _jev_col_section(doc: DocumentContext, _up: Upstream) -> dict[str, Any]:
    """Jev's relevance for every paragraph, the paragraphs retrieval would offer the audit, and Jev's pick at 0.5."""
    probabilities = await col_extractor.jev_paragraph_probabilities(doc.paragraphs)
    if all(p is None for p in probabilities):
        raise RuntimeError("Jev gave no paragraph answers; see the logged request error")
    retrieval = await retrieve_choice_of_law_candidates(doc)
    return {
        "col_sections": [text for text, p in zip(doc.paragraphs, probabilities, strict=True) if p is not None and p >= 0.5],
        "paragraph_probabilities": probabilities,
        "candidate_paragraphs": sorted({number for c in retrieval.candidates for number in c.paragraph_numbers}),
        "reasoning": jev_reasoning(config.JEV_MODEL, "paragraph relevance"),
    }


JEV_ONLY_RUNS: dict[str, Callable[[DocumentContext, Upstream], Awaitable[Any]]] = {
    "jurisdiction": _jev_jurisdiction,
    "themes": _jev_themes,
    "col_section": _jev_col_section,
}
GATE_SCORES = {"jurisdiction": "accuracy", "themes": "exact"}


def disable_jev_in_analyzer() -> None:
    """Make the analyzer steps skip Jev (as when unconfigured) while the judge keeps using it."""
    global JEV_ENABLED
    JEV_ENABLED = False

    async def unavailable(*_args: Any, **_kwargs: Any) -> None:
        return None

    for module in (col_extractor, jurisdiction_classifier, jurisdiction_detector, theme_classifier):
        module.ask_jev = unavailable  # type: ignore[attr-defined]


def _source_hash(step: Step) -> str:
    """Hash of the step's sources plus everything every step shares (prompts, utils, data, runner, models, Jev)."""
    shared = ("config.py", "runner.py", "validation.py", "jev.py", "tools/document_nav.py", "tools/models.py")
    shared_dirs = sorted(path for folder in ("prompts", "utils", "data") for path in (ANALYZER_DIR / folder).rglob("*"))
    files = [ANALYZER_DIR / name for name in (*step.sources, *shared)]
    files += [path for path in shared_dirs if path.is_file() and "__pycache__" not in path.parts]
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _cache_key(name: str, step: Step, entry: dict[str, Any]) -> str:
    payload = {
        "step": name,
        "model": [get_model(task) for task in (step.task, *step.extra_tasks)],
        "jev": JEV_ENABLED and bool(config.OPENROUTER_API_KEY) and config.JEV_MODEL,
        "jev_only": JEV_ONLY,
        "source": _source_hash(step),
        "text": entry["text"],
        "upstream": {key: entry["gold"][key] for key in step.requires},
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _dump(output: Any) -> dict[str, Any]:
    result = output.output if isinstance(output, StepResult) else output
    if isinstance(result, dict):
        return result
    return result.model_dump() if isinstance(result, BaseModel) else {"value": result}


def _cache_path(name: str, step: Step, entry: dict[str, Any]) -> Path:
    return CACHE_DIR / f"{_cache_key(name, step, entry)}.json"


def _answered_by(output: dict[str, Any]) -> str:
    return "jev" if answered_by_jev(str(output.get("reasoning", ""))) else "openai"


def make_task(name: str, step: Step, budget: Budget) -> Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]:
    async def task(entry: dict[str, Any]) -> dict[str, Any]:
        path = _cache_path(name, step, entry)
        if path.exists():
            cached = json.loads(path.read_text())
            set_eval_attribute("cached", True)
            set_eval_attribute("answered_by", _answered_by(cached["output"]))
            for metric, value in cached.get("metrics", {}).items():
                increment_eval_metric(metric, value)
            return cached["output"]
        budget.check()
        set_eval_attribute("cached", False)
        output = _dump(await step.run(DocumentContext(draft_id=0, text=entry["text"]), Upstream(entry["gold"])))
        set_eval_attribute("answered_by", _answered_by(output))
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"output": output}, ensure_ascii=False))
        return output

    return task


@dataclass
class CuratedMatch(Evaluator[dict[str, Any], dict[str, Any], dict[str, Any]]):
    """Scores the step output against the curated value (see evals.score)."""

    step: str

    async def evaluate(self, ctx: EvaluatorContext[dict[str, Any], dict[str, Any], dict[str, Any]]) -> EvaluatorOutput:
        return await score(self.step, ctx.output, ctx.inputs["gold"])


@dataclass
class SpendTracker(Evaluator[dict[str, Any], dict[str, Any], dict[str, Any]]):
    """Adds each new case's Logfire-priced cost to the budget and stores it with the cached output."""

    step: Step
    name: str
    budget: Budget

    def evaluate(self, ctx: EvaluatorContext[dict[str, Any], dict[str, Any], dict[str, Any]]) -> EvaluatorOutput:
        if ctx.attributes.get("cached"):
            return {}
        metrics = {metric: ctx.metrics[metric] for metric in METRICS if metric in ctx.metrics}
        self.budget.spent += metrics.get("cost", 0.0)
        if metrics.get("requests") and "cost" not in metrics:
            self.budget.unpriced_calls += int(metrics["requests"])
        path = _cache_path(self.name, self.step, ctx.inputs)
        if path.exists():
            path.write_text(json.dumps({"output": ctx.output, "metrics": metrics}, ensure_ascii=False))
        return {}


def build_dataset(name: str, step: Step, entries: list[dict[str, Any]], budget: Budget) -> Dataset[Any, Any, Any]:
    cases = [
        Case(
            name=str(entry["id"]),
            inputs=entry,
            metadata={"added_by": entry.get("added_by"), "jurisdiction": entry["gold"]["jurisdiction_code"]},
        )
        for entry in entries
        if all(entry["gold"][key] for key in step.requires)
    ]
    return Dataset(name=name, cases=cases, evaluators=[CuratedMatch(name), SpendTracker(step, name, budget)])


def _report_path(run_name: str, step: str) -> Path:
    return RUNS_DIR / f"{run_name}.{step}.json"


def load_report(run_name: str, step: str) -> EvaluationReport[Any, Any, Any] | None:
    path = _report_path(run_name, step)
    return EvaluationReportAdapter.validate_json(path.read_bytes()) if path.exists() else None


def total_cost(report: EvaluationReport[Any, Any, Any]) -> float:
    return sum(case.metrics.get("cost", 0.0) for case in report.cases)


def scores_by_answerer(report: EvaluationReport[Any, Any, Any]) -> dict[str, dict[str, float]]:
    """Case count and mean scores for the cases Jev answered and those OpenAI answered."""
    groups: dict[str, list[Any]] = {}
    for case in report.cases:
        groups.setdefault(str(case.attributes.get("answered_by", "openai")), []).append(case)
    summary: dict[str, dict[str, float]] = {}
    for answerer, cases in sorted(groups.items()):
        names = sorted({name for case in cases for name in case.scores})
        means = {
            name: sum(values) / len(values)
            for name in names
            if (values := [float(case.scores[name].value) for case in cases if name in case.scores])
        }
        summary[answerer] = {"cases": float(len(cases))} | means
    return summary


def theme_errors(report: EvaluationReport[Any, Any, Any]) -> dict[str, dict[str, int]]:
    """Per theme: curated count, predicted count, false positives and false negatives."""
    counts: dict[str, dict[str, int]] = {}
    for case in report.cases:
        gold, predicted = set(case.inputs["gold"]["themes"]), set(case.output.get("themes", [])) - {"NA"}
        for theme in gold | predicted:
            row = counts.setdefault(theme, {"curated": 0, "predicted": 0, "false_positive": 0, "false_negative": 0})
            row["curated"] += theme in gold
            row["predicted"] += theme in predicted
            row["false_positive"] += theme in predicted - gold
            row["false_negative"] += theme in gold - predicted
    return dict(sorted(counts.items(), key=lambda item: -item[1]["curated"]))


def pruning_table(report: EvaluationReport[Any, Any, Any]) -> list[tuple[str, float | None, float, float]]:
    """Per variant and threshold: mean share of the curated excerpt kept, and mean share of the text kept."""

    def row(variant: str, threshold: float | None, keep: Callable[[int, float | None, set[int]], bool]) -> tuple:
        recalls, shares = [], []
        for case in report.cases:
            paragraphs = DocumentContext(draft_id=0, text=case.inputs["text"]).paragraphs
            candidates = set(case.output["candidate_paragraphs"])
            probabilities = case.output["paragraph_probabilities"]
            kept = [
                text
                for number, (text, p) in enumerate(zip(paragraphs, probabilities, strict=True), start=1)
                if keep(number, p, candidates)
            ]
            recalls.append(excerpt_recall(kept, case.inputs["gold"]["col_excerpt"]))
            shares.append(sum(map(len, kept)) / max(1, sum(map(len, paragraphs))))
        return variant, threshold, sum(recalls) / len(recalls), sum(shares) / len(shares)

    if not report.cases:
        return []
    rows = [
        row("full text (ceiling)", None, lambda _n, _p, _c: True),
        row("retrieval candidates, no Jev", None, lambda number, _p, candidates: number in candidates),
    ]
    for threshold in PRUNING_THRESHOLDS:
        rows.append(row("Jev, all paragraphs", threshold, lambda _n, p, _c, t=threshold: p is not None and p >= t))
    for threshold in PRUNING_THRESHOLDS:
        rows.append(
            row(
                "Jev, within retrieval candidates",
                threshold,
                lambda number, p, candidates, t=threshold: number in candidates and p is not None and p >= t,
            )
        )
    return rows


def gate_table(report: EvaluationReport[Any, Any, Any], score_name: str) -> list[tuple[float, int, int, float | None]]:
    """Per threshold: cases Jev would answer, cases scored, and the mean score on the answered ones."""
    cases = [case for case in report.cases if score_name in case.scores]
    rows: list[tuple[float, int, int, float | None]] = []
    for threshold in GATE_THRESHOLDS:
        accepted = [case for case in cases if float(case.output.get("jev_confidence", 0.0)) >= threshold]
        mean = sum(float(case.scores[score_name].value) for case in accepted) / len(accepted) if accepted else None
        rows.append((threshold, len(accepted), len(cases), mean))
    return rows


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    parser.add_argument("--steps", default=",".join(STEPS), help=f"Comma-separated, from: {', '.join(STEPS)}")
    parser.add_argument("--name", required=True, help="Run name; reports go to analyzer-eval/runs/<name>.<step>.json")
    parser.add_argument("--models", default="{}", help='JSON overrides of TASK_MODELS, e.g. {"themes": "gpt-5.4-mini"}')
    parser.add_argument("--no-jev", action="store_true", help="Disable Jev in the analyzer steps (it still judges)")
    parser.add_argument(
        "--jev-only",
        action="store_true",
        help=f"Ask only Jev, without its confidence gate or OpenAI fallback ({', '.join(JEV_ONLY_RUNS)})",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-cost", type=float, default=None, help="Stop starting new model calls at this USD spend")
    parser.add_argument("--baseline", default=None, help="Name of an earlier run to compare against")
    args = parser.parse_args()

    global JEV_ONLY
    JEV_ONLY = args.jev_only
    names = args.steps.split(",")
    if args.jev_only:
        if not config.OPENROUTER_API_KEY:
            raise SystemExit("Set OPENROUTER_API_KEY in backend/.env; --jev-only calls Jev.")
        if unsupported := [name for name in names if name not in JEV_ONLY_RUNS]:
            raise SystemExit(f"--jev-only supports {', '.join(JEV_ONLY_RUNS)}, not {', '.join(unsupported)}")
        steps = {name: replace(STEPS[name], run=JEV_ONLY_RUNS[name]) for name in names}
    elif not config.OPENAI_API_KEY:
        raise SystemExit("Set OPENAI_API_KEY in backend/.env; the analyzer steps call OpenAI.")
    else:
        steps = {name: STEPS[name] for name in names}
    TASK_MODELS.update(json.loads(args.models))
    if args.no_jev:
        disable_jev_in_analyzer()
    configure_logfire()

    entries = corpus.load(args.split)
    entries = entries[: args.limit] if args.limit else entries
    budget = Budget(args.max_cost)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    for name, step in steps.items():
        dataset = build_dataset(name, step, entries, budget)
        report = await dataset.evaluate(
            make_task(name, step, budget),
            name=f"{args.name}: {name}",
            max_concurrency=args.concurrency,
            metadata={
                "split": args.split,
                "model": config.JEV_MODEL if JEV_ONLY else get_model(step.task),
                "jev": JEV_ENABLED,
                "jev_only": JEV_ONLY,
            },
        )
        _report_path(args.name, name).write_bytes(EvaluationReportAdapter.dump_json(report, indent=1))
        baseline = load_report(args.baseline, name) if args.baseline else None
        report.print(baseline=baseline, include_input=False, include_output=False, include_averages=True)
        stopped = sum(1 for failure in report.failures if "budget" in failure.error_message)
        model = config.JEV_MODEL if JEV_ONLY else get_model(step.task)
        line = f"{name} ({model}): configuration cost ${total_cost(report):.3f} over {len(report.cases)} cases"
        if baseline:
            line += f" (baseline ${total_cost(baseline):.3f})"
        print(line + (f"; {stopped} cases not run: budget reached" if stopped else ""))
        if name == "themes":
            print("  Per theme (curated / predicted / false positives / false negatives):")
            for theme, row in theme_errors(report).items():
                print(f"    {theme}: {row['curated']} / {row['predicted']} / {row['false_positive']} / {row['false_negative']}")
        if JEV_ONLY and name == "col_section":
            print("  Pruning (mean share of the curated excerpt kept / mean share of the text kept):")
            for variant, threshold, recall, share in pruning_table(report):
                at = f" >= {threshold:.1f}" if threshold is not None else ""
                print(f"    {variant}{at}: excerpt {recall:.0%}, text {share:.0%}")
            continue
        if JEV_ONLY:
            print(f"  Jev answers by confidence threshold ({GATE_SCORES[name]} on the answered cases):")
            for threshold, accepted, scored, mean in gate_table(report, GATE_SCORES[name]):
                share = f"{accepted}/{scored} ({accepted / scored:.0%})" if scored else "0/0"
                print(
                    f"    >= {threshold:.2f}: answers {share}"
                    + (f", {GATE_SCORES[name]} {mean:.2f}" if mean is not None else "")
                )
            continue
        by_answerer = scores_by_answerer(report)
        if "jev" in by_answerer:
            for answerer, stats in by_answerer.items():
                means = ", ".join(f"{name} {value:.2f}" for name, value in stats.items() if name != "cases")
                print(f"  answered by {answerer}: {int(stats['cases'])} cases; {means}")

    print(f"New model spend this run (OpenAI and Jev): ${budget.spent:.3f}")
    if budget.unpriced_calls:
        print(f"{budget.unpriced_calls} model calls had no price in genai-prices; their cost is missing above.")


if __name__ == "__main__":
    asyncio.run(main())
