"""Render an eval run as a markdown table, optionally against a baseline run."""

from collections import defaultdict
from statistics import mean
from typing import Any


def summarize(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_step: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in run["rows"]:
        by_step[row["step"]].append(row)
    summary: dict[str, dict[str, Any]] = {}
    for step, rows in by_step.items():
        scored = [row["scores"] for row in rows if row.get("scores")]
        metrics = sorted({metric for scores in scored for metric in scores})
        summary[step] = {
            "n": len(rows),
            "errors": sum(1 for row in rows if "error" in row),
            "cached": sum(1 for row in rows if row.get("cached")),
            "metrics": {m: mean(s[m] for s in scored if m in s) for m in metrics if any(m in s for s in scored)},
            "seconds": mean(row["seconds"] for row in rows if "seconds" in row) if any("seconds" in r for r in rows) else 0.0,
            "tokens": sum(r.get("usage", {}).get("input_tokens", 0) + r.get("usage", {}).get("output_tokens", 0) for r in rows),
            "cost": sum(r.get("usage", {}).get("cost", 0.0) for r in rows),
            "new_cost": sum(r.get("usage", {}).get("cost", 0.0) for r in rows if not r.get("cached")),
            "unpriced": sorted({m for r in rows for m in r.get("usage", {}).get("unpriced_models", [])}),
        }
    return summary


def _delta(value: float, baseline: float | None) -> str:
    if baseline is None:
        return f"{value:.2f}"
    diff = value - baseline
    return f"{value:.2f} ({'+' if diff >= 0 else ''}{diff:.2f})"


def render(run: dict[str, Any], baseline: dict[str, Any] | None = None) -> str:
    summary = summarize(run)
    base = summarize(baseline) if baseline else {}
    lines = [
        f"## Eval run `{run['name']}` — {run['split']} split, Jev {'on' if run['jev'] else 'off'}",
        "",
    ]
    if baseline:
        lines += [f"Compared with `{baseline['name']}` (differences in brackets).", ""]
    if run.get("stopped"):
        lines += [f"**Stopped early:** {run['stopped']}", ""]
    lines += [
        "| Step | Model | Decisions | Scores | Avg seconds | Tokens | Cost |",
        "|---|---|---|---|---|---|---|",
    ]
    for step, info in summary.items():
        before = base.get(step, {}).get("metrics", {})
        scores = ", ".join(f"{m} {_delta(v, before.get(m))}" for m, v in info["metrics"].items())
        cost = f"${info['cost']:.3f}"
        if step in base:
            cost += f" (was ${base[step]['cost']:.3f})"
        if info["unpriced"]:
            cost += f"; no price for {', '.join(info['unpriced'])}"
        counts = f"{info['n']} ({info['cached']} cached, {info['errors']} errors)"
        lines.append(
            f"| {step} | {run['models'].get(step, '')} | {counts} | {scores} | {info['seconds']:.1f} | "
            f"{info['tokens']:,} | {cost} |"
        )
    total = sum(info["cost"] for info in summary.values())
    new = sum(info["new_cost"] for info in summary.values())
    lines += [
        "",
        f"Cost of this configuration over these decisions: ${total:.3f}; actually spent this run: ${new:.3f} "
        "(the rest came from the cache).",
    ]
    lines += ["Free-text steps are judged by Jev against the curated text: `agreement` is its mean probability."]
    return "\n".join(lines) + "\n"
