"""Evaluate Jev against curated CoLD court decisions.

Pulls every court decision from the public CoLD API and runs two experiments:

- themes: Jev's per-theme probabilities (the exact questions the analyzer asks) against the
  curated themes, once per input text (the CoL excerpt, and the original text).
- paragraphs: Jev's yes/no "is this paragraph choice-of-law reasoning?" for every paragraph
  of the original text, labelled relevant when the paragraph overlaps the curated CoL excerpt.

Writes corpus.jsonl, per-item predictions and report.md to --out.

    OPENROUTER_API_KEY=... uv run python scripts/jev_eval.py --limit 100
"""

import argparse
import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from typing import Any, get_args

import httpx2
from rapidfuzz import fuzz

from app.case_analyzer.jev import JEV_MIN_CONFIDENCE, NoulAnswer, ask_jev, noul_question
from app.case_analyzer.tools.models import Theme
from app.case_analyzer.tools.theme_classifier import jev_theme_probabilities

THEMES: tuple[Theme, ...] = get_args(Theme)
THEME_BY_KEY = {theme.casefold(): theme for theme in THEMES}
THEME_TEXT_FIELDS = {
    "excerpt": ("quote",),
    "issue_and_position": ("choiceoflawissue", "courtsposition"),
    "original_text": ("originaltext",),
}
COVERAGE_FIELDS = (
    "themes",
    "quote",
    "translatedexcerpt",
    "choiceoflawissue",
    "courtsposition",
    "originaltext",
    "englishtranslation",
    "abstract",
)
THRESHOLDS = (0.3, 0.5, 0.7, 0.9)
PARAGRAPH_MIN_CHARS = 40
PARAGRAPH_MATCH_SCORE = 85
PARAGRAPH_QUESTION = noul_question(
    "Does this paragraph contain the court's reasoning or holding on which law governs the dispute (choice of law)?",
    true="The paragraph states, applies or reasons about the applicable law, a choice-of-law clause, or a conflict-of-laws rule.",
    false="The paragraph covers facts, procedure, costs or substantive issues without addressing which law applies.",
)


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {_key(name): value for name, value in record.items()}


def _field(record: dict[str, Any], name: str) -> str:
    value = record.get(name)
    if isinstance(value, str) and value.strip() and value.strip().casefold() not in {"na", "n/a", "not found"}:
        return value.strip()
    return ""


def _text(record: dict[str, Any], *fields: str) -> str:
    return "\n\n".join(text for name in fields if (text := _field(record, name)))


def _theme_name(value: Any) -> str:
    if isinstance(value, dict):
        for name in ("theme", "title", "name", "value"):
            if isinstance(value.get(name), str):
                return value[name]
    return str(value)


def gold_themes(record: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Curated themes the analyzer knows, and any it does not."""
    raw = record.get("themes") or []
    names = raw if isinstance(raw, list) else re.split(r"[,;]", str(raw))
    known: set[str] = set()
    unknown: set[str] = set()
    for name in (_theme_name(n).strip() for n in names):
        if not name:
            continue
        theme = THEME_BY_KEY.get(name.casefold())
        (known if theme else unknown).add(theme or name)
    return known, unknown


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold().strip()


def _paragraph_source(record: dict[str, Any]) -> tuple[str, str] | None:
    """Full text and its curated CoL excerpt, in the original language or else in English."""
    for full_field, excerpt_field in (("originaltext", "quote"), ("englishtranslation", "translatedexcerpt")):
        full_text, excerpt = _field(record, full_field), _field(record, excerpt_field)
        if full_text and excerpt:
            return full_text, excerpt
    return None


def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n", text) if "\n\n" in text else text.split("\n")
    return [p.strip() for p in parts if len(p.strip()) >= PARAGRAPH_MIN_CHARS]


async def fetch_corpus(api_base: str) -> list[dict[str, Any]]:
    async with httpx2.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{api_base}/api/v1/search/full_table", params={"table": "Court Decisions"})
        response.raise_for_status()
        return [normalize_record(r) for r in response.json()]


async def gather_limited[T](jobs: Iterable[Callable[[], Awaitable[T]]], concurrency: int) -> list[T]:
    semaphore = asyncio.Semaphore(concurrency)

    async def run(job: Callable[[], Awaitable[T]]) -> T:
        async with semaphore:
            return await job()

    return await asyncio.gather(*(run(job) for job in jobs))


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def coverage_report(corpus: list[dict[str, Any]]) -> str:
    lines = [
        "### Corpus fields",
        "",
        "| Field | Filled | Usable text | + any curated theme | + analyzer theme |",
        "|---|---|---|---|---|",
    ]
    for name in COVERAGE_FIELDS + ("relevantfacts", "officialsourcepdf", "officialsourceurl"):
        filled = sum(1 for r in corpus if r.get(name) not in (None, "", [], {}))
        usable = [r for r in corpus if _field(r, name)]
        any_theme = sum(1 for r in usable if any(gold_themes(r)))
        known_theme = sum(1 for r in usable if gold_themes(r)[0])
        lines.append(f"| `{name}` | {filled} | {len(usable)} | {any_theme} | {known_theme} |")
    lines += ["", f"{len(corpus)} decisions in total."]

    counts: dict[str, int] = {}
    for record in corpus:
        for theme in gold_themes(record)[1]:
            counts[theme] = counts.get(theme, 0) + 1
    if counts:
        ranked = sorted(counts.items(), key=lambda item: -item[1])
        lines += ["", "Curated themes outside the analyzer's 12: " + ", ".join(f"{t} ({n})" for t, n in ranked)]
    samples = {
        name: json.dumps(next((r[name] for r in corpus if r.get(name)), None), ensure_ascii=False, default=str)[:150]
        for name in ("themes", "originaltext", "officialsourcepdf")
    }
    lines += ["", *(f"Sample `{name}`: `{value}`" for name, value in samples.items())]
    return "\n".join(lines)


async def evaluate_themes(
    corpus: list[dict[str, Any]], variant: str, limit: int | None, concurrency: int
) -> tuple[list[dict[str, Any]], str]:
    items = []
    for record in corpus:
        known, unknown = gold_themes(record)
        text = _text(record, *THEME_TEXT_FIELDS[variant])
        if known and text:
            items.append({"id": record.get("id"), "gold": sorted(known), "unmapped_gold": sorted(unknown), "text": text})
    items = items[:limit] if limit else items

    async def predict(item: dict[str, Any]) -> dict[str, Any]:
        result = await jev_theme_probabilities(item["text"])
        return {**item, "probabilities": result[1] if result else None}

    rows = await gather_limited([lambda item=item: predict(item) for item in items], concurrency)
    scored = [r for r in rows if r["probabilities"] is not None]

    lines = [f"### Themes — input: `{variant}`", ""]
    lines.append(f"{len(items)} decisions with curated themes and text; {len(items) - len(scored)} Jev failures.")
    if not scored:
        return rows, "\n".join(lines)

    lines += ["", "| Threshold | Precision | Recall | F1 | Exact match |", "|---|---|---|---|---|"]
    for threshold in THRESHOLDS:
        tp = fp = fn = exact = 0
        for row in scored:
            predicted = {t for t, p in row["probabilities"].items() if p >= threshold}
            gold = set(row["gold"])
            tp += len(predicted & gold)
            fp += len(predicted - gold)
            fn += len(gold - predicted)
            exact += predicted == gold
        p, r, f = _prf(tp, fp, fn)
        lines.append(f"| {threshold} | {p:.2f} | {r:.2f} | {f:.2f} | {exact / len(scored):.0%} |")

    lines += ["", "| Theme | Support | Precision | Recall | F1 |", "|---|---|---|---|---|"]
    for theme in THEMES:
        tp = sum(1 for r in scored if r["probabilities"][theme] >= 0.5 and theme in r["gold"])
        fp = sum(1 for r in scored if r["probabilities"][theme] >= 0.5 and theme not in r["gold"])
        fn = sum(1 for r in scored if r["probabilities"][theme] < 0.5 and theme in r["gold"])
        p, r, f = _prf(tp, fp, fn)
        lines.append(f"| {theme} | {tp + fn} | {p:.2f} | {r:.2f} | {f:.2f} |")

    lines += ["", "Analyzer gate (all themes decisive, at least one yes):", ""]
    lines += ["| Gate | Accepted | Exact match on accepted |", "|---|---|---|"]
    for gate in (0.6, 0.7, JEV_MIN_CONFIDENCE, 0.9):
        accepted = [
            r
            for r in scored
            if min(max(p, 1 - p) for p in r["probabilities"].values()) >= gate
            and any(p >= 0.5 for p in r["probabilities"].values())
        ]
        exact = sum({t for t, p in r["probabilities"].items() if p >= 0.5} == set(r["gold"]) for r in accepted)
        rate = f"{exact / len(accepted):.0%}" if accepted else "–"
        lines.append(f"| {gate} | {len(accepted)}/{len(scored)} ({len(accepted) / len(scored):.0%}) | {rate} |")

    unmapped = sorted({t for r in rows for t in r["unmapped_gold"]})
    if unmapped:
        lines += ["", f"Curated themes the analyzer does not model (ignored): {', '.join(unmapped)}"]
    return rows, "\n".join(lines)


async def evaluate_paragraphs(
    corpus: list[dict[str, Any]], limit: int | None, concurrency: int
) -> tuple[list[dict[str, Any]], str]:
    items = []
    best_scores: list[float] = []
    usable = [(r, source) for r in corpus if (source := _paragraph_source(r))]
    for record, (full_text, excerpt) in usable[:limit] if limit else usable:
        excerpt_key = _normalize(excerpt)
        paragraphs = split_paragraphs(full_text)
        scores = [fuzz.partial_ratio(_normalize(p), excerpt_key) for p in paragraphs]
        best_scores.append(max(scores, default=0.0))
        for index, (paragraph, score) in enumerate(zip(paragraphs, scores, strict=True)):
            relevant = score >= PARAGRAPH_MATCH_SCORE
            items.append({"id": record.get("id"), "index": index, "relevant": relevant, "match": score, "text": paragraph})

    async def predict(item: dict[str, Any]) -> dict[str, Any]:
        response = await ask_jev("paragraph_relevance", item["text"], {"relevant": PARAGRAPH_QUESTION})
        answer = response.answers.get("relevant") if response else None
        return {**item, "probability": answer.noul if isinstance(answer, NoulAnswer) else None}

    rows = await gather_limited([lambda item=item: predict(item) for item in items], concurrency)
    scored = [r for r in rows if r["probability"] is not None]
    decisions = {r["id"] for r in rows}
    positives = sum(r["relevant"] for r in scored)

    lines = ["### Paragraph relevance", ""]
    if best_scores:
        ordered = sorted(best_scores)
        lines.append(
            f"Best paragraph-to-excerpt match per decision: median {ordered[len(ordered) // 2]:.0f}, "
            f"min {ordered[0]:.0f}, max {ordered[-1]:.0f} (relevant at ≥ {PARAGRAPH_MATCH_SCORE})."
        )
        lines.append("")
    lines.append(
        f"{len(rows)} paragraphs from {len(decisions)} decisions ({positives} overlap the curated excerpt); "
        f"{len(rows) - len(scored)} Jev failures."
    )
    if not scored:
        return rows, "\n".join(lines)
    lines += ["", "| Threshold | Precision | Recall | F1 | Paragraphs flagged |", "|---|---|---|---|---|"]
    for threshold in THRESHOLDS:
        tp = sum(1 for r in scored if r["probability"] >= threshold and r["relevant"])
        fp = sum(1 for r in scored if r["probability"] >= threshold and not r["relevant"])
        fn = sum(1 for r in scored if r["probability"] < threshold and r["relevant"])
        p, r, f = _prf(tp, fp, fn)
        lines.append(f"| {threshold} | {p:.2f} | {r:.2f} | {f:.2f} | {(tp + fp) / len(scored):.0%} |")

    hits = 0
    ranked_decisions = 0
    for decision in decisions:
        paragraphs = [r for r in scored if r["id"] == decision]
        if not any(r["relevant"] for r in paragraphs):
            continue
        ranked_decisions += 1
        top = sorted(paragraphs, key=lambda r: r["probability"], reverse=True)[:3]
        hits += any(r["relevant"] for r in top)
    if ranked_decisions:
        lines += [
            "",
            f"A relevant paragraph is in Jev's top 3 for {hits}/{ranked_decisions} decisions ({hits / ranked_decisions:.0%}).",
        ]
    return rows, "\n".join(lines)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, default=str) + "\n" for row in rows))


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api-base", default="https://api.cold.global")
    parser.add_argument("--experiments", default="themes,paragraphs")
    parser.add_argument("--limit", type=int, default=None, help="Evaluate at most this many decisions")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--out", type=Path, default=Path("jev-eval"))
    args = parser.parse_args()
    experiments = set(args.experiments.split(","))

    probe = await ask_jev(
        "probe", "I was charged twice for my subscription.", {"refund": noul_question("Is the customer asking for money back?")}
    )
    if probe is None:
        raise SystemExit("Jev probe request failed; see the warning above for OpenRouter's error.")

    args.out.mkdir(parents=True, exist_ok=True)
    corpus = await fetch_corpus(args.api_base)
    write_jsonl(args.out / "corpus.jsonl", corpus)

    sections = [
        "## Jev evaluation",
        "",
        f"{len(corpus)} court decisions fetched from {args.api_base}; "
        f"up to {args.limit or 'all'} usable decisions evaluated per experiment.",
        "",
        coverage_report(corpus),
    ]
    if "themes" in experiments:
        for variant in THEME_TEXT_FIELDS:
            rows, report = await evaluate_themes(corpus, variant, args.limit, args.concurrency)
            write_jsonl(args.out / f"themes_{variant}.jsonl", rows)
            sections += ["", report]
    if "paragraphs" in experiments:
        rows, report = await evaluate_paragraphs(corpus, args.limit, args.concurrency)
        write_jsonl(args.out / "paragraphs.jsonl", rows)
        sections += ["", report]

    report_text = "\n".join(sections) + "\n"
    (args.out / "report.md").write_text(report_text)
    print(report_text)


if __name__ == "__main__":
    asyncio.run(main())
