"""Run analyzer steps over the eval corpus and score them against curated values.

Each step is run in isolation: its upstream inputs (CoL section, themes, CoL issue, ...) are
the curated values, so testing one step never pays for the steps before it, and a weak
upstream step cannot drag a downstream score down. Step outputs are cached on disk by step,
model, analyzer source and input, so re-runs only pay for what changed.

    uv run python -m evals.run --split dev --steps themes,col_issue --name baseline \\
        --prices evals/prices.json --max-cost 2
    uv run python -m evals.run --split dev --steps themes --name mini \\
        --models '{"themes": "gpt-5.4-mini"}' --baseline baseline
"""

import argparse
import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents import set_tracing_disabled
from pydantic import BaseModel

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

from . import corpus, report, usage
from .score import score

JEV_ENABLED = True
RUNS_DIR = corpus.EVAL_DIR / "runs"
CACHE_DIR = corpus.EVAL_DIR / "cache"
ANALYZER_DIR = Path(__file__).resolve().parent.parent / "app" / "case_analyzer"


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


async def run_one(name: str, step: Step, entry: dict[str, Any], tracker: usage.UsageTracker) -> dict[str, Any]:
    cache_path = CACHE_DIR / f"{_cache_key(name, step, entry)}.json"
    row: dict[str, Any] = {"id": entry["id"], "step": name, "model": get_model(step.task)}
    if cache_path.exists():
        cached = json.loads(cache_path.read_text())
        row.update(output=cached["output"], seconds=cached["seconds"], usage=cached.get("usage", {}), cached=True)
    else:
        tracker.check_budget()
        usage.current_step.set(name)
        row_usage = usage.StepUsage()
        usage.current_row.set(row_usage)
        started = time.monotonic()
        try:
            output = await step.run(DocumentContext(draft_id=0, text=entry["text"]), Upstream(entry["gold"]))
        except usage.BudgetExceeded:
            raise
        except Exception as e:
            row.update(error=f"{type(e).__name__}: {e}"[:500])
            return row
        row_usage.unpriced_models = sorted(row_usage.unpriced_models)  # type: ignore[assignment]
        row.update(output=_dump(output), seconds=round(time.monotonic() - started, 1), usage=vars(row_usage), cached=False)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cached = {"output": row["output"], "seconds": row["seconds"], "usage": row["usage"]}
        cache_path.write_text(json.dumps(cached, ensure_ascii=False))
    row["scores"] = await score(name, row["output"], entry["gold"])
    return row


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    parser.add_argument("--steps", default=",".join(STEPS), help=f"Comma-separated, from: {', '.join(STEPS)}")
    parser.add_argument("--name", required=True, help="Run name; results go to analyzer-eval/runs/<name>.json")
    parser.add_argument("--models", default="{}", help='JSON overrides of TASK_MODELS, e.g. {"themes": "gpt-5.4-mini"}')
    parser.add_argument("--no-jev", action="store_true", help="Disable Jev in the analyzer steps (it still judges)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--prices", type=Path, default=Path("evals/prices.json"))
    parser.add_argument("--max-cost", type=float, default=None, help="Stop starting new OpenAI calls above this USD")
    parser.add_argument("--baseline", default=None, help="Name of an earlier run to compare against")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        raise SystemExit("Set OPENAI_API_KEY in backend/.env; the analyzer steps call OpenAI.")
    steps = {name: STEPS[name] for name in args.steps.split(",")}
    TASK_MODELS.update(json.loads(args.models))
    set_tracing_disabled(True)
    tracker = usage.UsageTracker(usage.load_prices(args.prices if args.prices.exists() else None), args.max_cost)
    usage.install(tracker)
    if args.no_jev:
        disable_jev_in_analyzer()

    entries = corpus.load(args.split)[: args.limit] if args.limit else corpus.load(args.split)
    jobs = [
        (name, step, entry)
        for name, step in steps.items()
        for entry in entries
        if all(entry["gold"][key] for key in step.requires)
    ]
    print(
        f"{len(jobs)} step runs over {len(entries)} {args.split} decisions; models: "
        + ", ".join(f"{name}={get_model(step.task)}" for name, step in steps.items())
    )

    semaphore = asyncio.Semaphore(args.concurrency)
    rows: list[dict[str, Any]] = []
    stopped: str | None = None

    async def worker(name: str, step: Step, entry: dict[str, Any]) -> None:
        nonlocal stopped
        if stopped:
            return
        async with semaphore:
            if stopped:
                return
            try:
                rows.append(await run_one(name, step, entry, tracker))
            except usage.BudgetExceeded as e:
                stopped = str(e)

    await asyncio.gather(*(worker(*job) for job in jobs))

    run = {
        "name": args.name,
        "split": args.split,
        "models": {name: get_model(step.task) for name, step in steps.items()},
        "jev": not args.no_jev,
        "stopped": stopped,
        "usage": {
            name: vars(step_usage) | {"unpriced_models": sorted(step_usage.unpriced_models)}
            for name, step_usage in tracker.steps.items()
        },
        "rows": rows,
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / f"{args.name}.json").write_text(json.dumps(run, ensure_ascii=False, indent=1, default=str))

    baseline = json.loads((RUNS_DIR / f"{args.baseline}.json").read_text()) if args.baseline else None
    text = report.render(run, baseline)
    (RUNS_DIR / f"{args.name}.md").write_text(text)
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
