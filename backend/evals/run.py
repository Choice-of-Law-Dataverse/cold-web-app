"""Run analyzer steps over the eval corpus as pydantic-evals experiments.

Each step is run in isolation: its upstream inputs (CoL section, themes, CoL issue, ...) are
the curated values, so testing one step never pays for the steps before it, and a weak
upstream step cannot drag a downstream score down. Step outputs are cached on disk by step,
model, analyzer source and input, so re-runs only pay for what changed. Cost per case comes
from Logfire's pricing of each model call; cached cases report the cost recorded when they ran.

    uv run python -m evals.run --split dev --steps themes,col_issue --name baseline --max-cost 2
    uv run python -m evals.run --split dev --steps themes --name mini \\
        --models '{"themes": "gpt-5.4-mini"}' --baseline baseline
"""

import argparse
import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_evals import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput
from pydantic_evals.reporting import EvaluationReport, EvaluationReportAdapter

from app.case_analyzer.config import TASK_MODELS, get_model
from app.case_analyzer.service import detect_jurisdiction
from app.case_analyzer.tools import (
    classify_themes,
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
from .score import score

JEV_ENABLED = True
RUNS_DIR = corpus.EVAL_DIR / "runs"
CACHE_DIR = corpus.EVAL_DIR / "cache"
ANALYZER_DIR = Path(__file__).resolve().parent.parent / "app" / "case_analyzer"
METRICS = ("cost", "input_tokens", "output_tokens", "requests")


class Upstream:
    """Curated values in the shapes the analyzer steps take as inputs."""

    def __init__(self, gold: dict[str, Any]) -> None:
        self.gold = gold
        self.jurisdiction = gold["jurisdiction"] or None
        self.legal_system = detect_legal_system_by_jurisdiction(gold["jurisdiction"]) or "Civil-law jurisdiction"
        self.col = ColSectionOutput(col_sections=[gold["col_excerpt"]], confidence="high", reasoning="Curated")
        self.themes = ThemeClassificationOutput(themes=gold["themes"] or ["NA"], confidence="high", reasoning="Curated")
        self.facts = RelevantFactsOutput(relevant_facts=gold["relevant_facts"], confidence="high", reasoning="Curated")
        self.provisions = PILProvisionsOutput(pil_provisions=gold["pil_provisions"], confidence="high", reasoning="Curated")
        self.issue = ColIssueOutput(col_issue=gold["col_issue"], confidence="high", reasoning="Curated")
        self.position = CourtsPositionOutput(courts_position=gold["courts_position"], confidence="high", reasoning="Curated")


@dataclass(frozen=True)
class Step:
    task: str
    requires: tuple[str, ...]
    run: Callable[[DocumentContext, Upstream], Awaitable[Any]]
    module: str


async def _jurisdiction(doc: DocumentContext, _up: Upstream) -> Any:
    return await detect_jurisdiction(doc.text)


STEPS: dict[str, Step] = {
    "jurisdiction": Step("jurisdiction_classification", ("jurisdiction_code",), _jurisdiction, "jurisdiction_classifier"),
    "col_section": Step("col_section", ("col_excerpt",), lambda doc, up: extract_col_section(doc), "col_extractor"),
    "themes": Step(
        "themes",
        ("col_excerpt", "themes"),
        lambda doc, up: classify_themes(doc, up.gold["col_excerpt"], up.legal_system, up.jurisdiction),
        "theme_classifier",
    ),
    "case_citation": Step(
        "case_citation",
        ("case_citation",),
        lambda doc, up: extract_case_citation(doc, up.legal_system, up.jurisdiction or ""),
        "case_citation_extractor",
    ),
    "pil_provisions": Step(
        "pil_provisions",
        ("col_excerpt", "pil_provisions"),
        lambda doc, up: extract_pil_provisions(doc, up.col, up.legal_system, up.jurisdiction),
        "pil_provisions_extractor",
    ),
    "relevant_facts": Step(
        "relevant_facts",
        ("col_excerpt", "relevant_facts"),
        lambda doc, up: extract_relevant_facts(doc, up.col, up.legal_system, up.jurisdiction),
        "relevant_facts_extractor",
    ),
    "col_issue": Step(
        "col_issue",
        ("col_excerpt", "themes", "col_issue"),
        lambda doc, up: extract_col_issue(doc, up.col, up.legal_system, up.jurisdiction, up.themes),
        "col_issue_extractor",
    ),
    "courts_position": Step(
        "courts_position",
        ("col_excerpt", "themes", "col_issue", "courts_position"),
        lambda doc, up: extract_courts_position(doc, up.col, up.legal_system, up.jurisdiction, up.themes, up.issue),
        "courts_position_extractor",
    ),
    "abstract": Step(
        "abstract",
        ("themes", "relevant_facts", "pil_provisions", "col_issue", "courts_position", "abstract"),
        lambda doc, up: extract_abstract(
            doc, up.legal_system, up.jurisdiction, up.themes, up.facts, up.provisions, up.issue, up.position
        ),
        "abstract_generator",
    ),
}


def disable_jev_in_analyzer() -> None:
    """Make the analyzer steps skip Jev (as when unconfigured) while the judge keeps using it."""
    global JEV_ENABLED
    JEV_ENABLED = False

    async def unavailable(*_args: Any, **_kwargs: Any) -> None:
        return None

    for module in (jurisdiction_classifier, jurisdiction_detector, theme_classifier):
        module.ask_jev = unavailable  # type: ignore[attr-defined]


def _source_hash(step: Step) -> str:
    """Hash of the step's module plus everything every step shares (prompts, runner, models, Jev)."""
    shared = [ANALYZER_DIR / name for name in ("runner.py", "validation.py", "jev.py", "tools/models.py")]
    files = [ANALYZER_DIR / "tools" / f"{step.module}.py", *shared, *sorted((ANALYZER_DIR / "prompts").rglob("*.py"))]
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _cache_key(name: str, step: Step, entry: dict[str, Any]) -> str:
    payload = {
        "step": name,
        "model": get_model(step.task),
        "jev": JEV_ENABLED and bool(config.OPENROUTER_API_KEY) and config.JEV_MODEL,
        "source": _source_hash(step),
        "text": entry["text"],
        "upstream": {key: entry["gold"][key] for key in step.requires},
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _dump(output: Any) -> dict[str, Any]:
    result = output.output if isinstance(output, StepResult) else output
    return result.model_dump() if isinstance(result, BaseModel) else {"value": result}


def _cache_path(name: str, step: Step, entry: dict[str, Any]) -> Path:
    return CACHE_DIR / f"{_cache_key(name, step, entry)}.json"


def make_task(name: str, step: Step, budget: Budget) -> Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]:
    async def task(entry: dict[str, Any]) -> dict[str, Any]:
        path = _cache_path(name, step, entry)
        if path.exists():
            cached = json.loads(path.read_text())
            set_eval_attribute("cached", True)
            for metric, value in cached.get("metrics", {}).items():
                increment_eval_metric(metric, value)
            return cached["output"]
        budget.check()
        set_eval_attribute("cached", False)
        output = _dump(await step.run(DocumentContext(draft_id=0, text=entry["text"]), Upstream(entry["gold"])))
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


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    parser.add_argument("--steps", default=",".join(STEPS), help=f"Comma-separated, from: {', '.join(STEPS)}")
    parser.add_argument("--name", required=True, help="Run name; reports go to analyzer-eval/runs/<name>.<step>.json")
    parser.add_argument("--models", default="{}", help='JSON overrides of TASK_MODELS, e.g. {"themes": "gpt-5.4-mini"}')
    parser.add_argument("--no-jev", action="store_true", help="Disable Jev in the analyzer steps (it still judges)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-cost", type=float, default=None, help="Stop starting new OpenAI calls at this USD spend")
    parser.add_argument("--baseline", default=None, help="Name of an earlier run to compare against")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        raise SystemExit("Set OPENAI_API_KEY in backend/.env; the analyzer steps call OpenAI.")
    steps = {name: STEPS[name] for name in args.steps.split(",")}
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
            metadata={"split": args.split, "model": get_model(step.task), "jev": JEV_ENABLED},
        )
        _report_path(args.name, name).write_bytes(EvaluationReportAdapter.dump_json(report, indent=1))
        baseline = load_report(args.baseline, name) if args.baseline else None
        report.print(baseline=baseline, include_input=False, include_output=False, include_averages=True)
        stopped = sum(1 for failure in report.failures if "budget" in failure.error_message)
        line = f"{name} ({get_model(step.task)}): configuration cost ${total_cost(report):.3f} over {len(report.cases)} cases"
        if baseline:
            line += f" (baseline ${total_cost(baseline):.3f})"
        print(line + (f"; {stopped} cases not run: budget reached" if stopped else ""))

    print(f"New OpenAI spend this run: ${budget.spent:.3f}")
    if budget.unpriced_calls:
        print(f"{budget.unpriced_calls} model calls had no price in genai-prices; their cost is missing above.")


if __name__ == "__main__":
    asyncio.run(main())
