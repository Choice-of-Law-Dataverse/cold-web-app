# Case analyzer evals

A local harness, built on [pydantic-evals](https://pydantic.dev/docs/ai/evals/evals/), for measuring each case analyzer step against the curated values in the CoLD
database, so prompt and model changes (including OpenAI upgrades and Jev) are decided on numbers.

## Setup

`backend/.env` needs `OPENAI_API_KEY` (the steps) and `OPENROUTER_API_KEY` (Jev, used in the
steps and as the judge for free-text answers). Everything is written to `backend/analyzer-eval/`,
which git ignores; reports are saved as `runs/<name>.<step>.json` for later baselines.

Cost needs no configuration: Logfire's OpenAI Agents instrumentation prices every model call
from `genai-prices`, and pydantic-evals reports it as each case's `cost` metric. With
`LOGFIRE_TOKEN` set, every run also appears in Logfire as an experiment you can compare there.
A model too new for the installed `genai-prices` shows tokens but no cost; the run says so.

## Build the corpus

```bash
uv run python -m evals.corpus --dev-size 30
```

Takes every court decision with full text and a curated CoL analysis from the public API and
splits them deterministically: a small `dev` set for iterating and a held-out `test` set for
model decisions. `added_by` is kept so decisions entered through the analyzer itself can be
excluded; they would reward the current models for matching their own output.

## Run

```bash
# Baseline on the dev set, capped at $2 of new OpenAI spend (one experiment per step)
uv run python -m evals.run --split dev --name baseline --max-cost 2

# One step with a different model, compared with the baseline
uv run python -m evals.run --split dev --steps themes --models '{"themes": "gpt-5.4-mini"}' \
  --name themes-mini --baseline baseline

# Same, with the Jev-first path in the analyzer switched off
uv run python -m evals.run --split dev --steps themes --no-jev --name themes-no-jev --baseline baseline
```

Keeping cost down:

- **Isolated steps.** Each step gets the curated upstream values as input (CoL excerpt, themes,
  CoL issue, …), so evaluating `col_issue` never re-runs CoL extraction.
- **Cache.** Outputs are cached by step, model, analyzer source, input and Jev setting, together
  with the cost they had. Re-runs only pay for what changed, while each report still shows the
  configuration's full cost; the run ends with what was actually spent.
- **Budget.** `--max-cost` stops starting new calls once the run's new spend passes the limit.
- **Dev first.** Iterate on `dev` (30 decisions); run `test` only to confirm a decision.

## Scores

| Step | Score |
|---|---|
| jurisdiction | Alpha-3 code accuracy |
| col_section | How much of the curated excerpt is recovered, and output length relative to it |
| themes | Precision / recall / F1 against the curated themes |
| pil_provisions | Fuzzy precision / recall / F1 |
| case_citation | Normalized match |
| relevant_facts, col_issue, courts_position, abstract | Jev's probability that the answer agrees with the curated text |

Obiter dicta and dissenting opinions have no curated values and are not scored.
