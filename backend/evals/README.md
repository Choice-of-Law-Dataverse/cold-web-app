# Case analyzer evals

A local harness, built on [pydantic-evals](https://pydantic.dev/docs/ai/evals/evals/), for measuring each case analyzer step against the curated values in the CoLD
database, so prompt and model changes (including OpenAI upgrades and Jev) are decided on numbers.

## Setup

`backend/.env` needs `OPENAI_API_KEY` (the steps) and `OPENROUTER_API_KEY` (Jev, used in the
steps and as the judge for free-text answers). Everything is written to `backend/analyzer-eval/`,
which git ignores; reports are saved as `runs/<name>.<step>.json` for later baselines.

Cost needs no configuration: Logfire's OpenAI Agents instrumentation prices every OpenAI call
from `genai-prices`, the Jev client records the cost OpenRouter reports for each Jev call, and
pydantic-evals reports their sum as each case's `cost` metric. Jev's cost as a judge is not part
of a step's cost. With
`LOGFIRE_TOKEN` set, every run also appears in Logfire as an experiment you can compare there.
A model too new for the installed `genai-prices` shows tokens but no cost; the run says so.

## Build the corpus

```bash
# Optional: text from the official PDFs, for decisions with no Original_Text (slow; read-only)
uv run python scripts/extract_court_decision_texts.py --out analyzer-eval/texts.jsonl

uv run python -m evals.corpus --texts analyzer-eval/texts.jsonl
```

Takes every court decision with full text (Original_Text, the English translation, or the PDF
text) and at least one curated value from the public API. Each step runs only on the decisions
that have its curated values, so PDF text mainly grows the `jurisdiction` step. A hash of each
decision's ID puts it in `dev` (iterating) or the held-out `test` set (model decisions), half
each by default (`--dev-share`); adding decisions never moves one between sets.

The public API does not expose who entered a decision, so decisions entered through the
analyzer itself cannot be excluded yet. Their curated values may be edited analyzer output,
which favours the current OpenAI setup.

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

Validate Jev on its own first; it costs a fraction of a cent per decision and needs no OpenAI key:

```bash
uv run python -m evals.run --split dev --steps jurisdiction,themes --jev-only --name jev
```

`--jev-only` asks Jev every case with no confidence gate and no OpenAI fallback, and prints,
per confidence threshold, how many cases Jev would answer and its accuracy on them (for themes,
exact matches of the curated set). That shows whether the analyzer's 0.8 gate is worth keeping
before paying OpenAI for the cases Jev leaves.

Every case records whether Jev or OpenAI answered it (the `answered_by` attribute). For the
Jev-first steps (`jurisdiction`, `themes`) the run prints the scores of each group, which is the
number the confidence gate is set by: compare Jev's group with the same cases in a `--no-jev` run.

Keeping cost down:

- **Isolated steps.** Each step gets the curated upstream values as input (CoL excerpt, themes,
  CoL issue, …), so evaluating `col_issue` never re-runs CoL extraction.
- **Cache.** Outputs are cached by step, model, analyzer source, input and Jev setting, together
  with the cost they had. Re-runs only pay for what changed, while each report still shows the
  configuration's full cost; the run ends with what was actually spent.
- **Budget.** `--max-cost` stops starting new calls once the run's new spend passes the limit.
- **Dev first.** Iterate on `dev`; run `test` only to confirm a decision.

## What a step sees

A case's `inputs` hold only the decision text and the curated values the step is designed to take as input
(`Step.uses`, plus the curated jurisdiction for jurisdiction-specific prompts). The value it is scored against
(`Step.target`) is the case's `expected_output`, which pydantic-evals passes to the evaluators but never to the
task; a step that reads a curated value it does not declare fails with `KeyError`. The jurisdiction step gets the
text alone. Cases are named by decision ID (for example `CD-ARE-1138`, which contains the country code) so results
can be traced back, but the task never receives the name or the metadata. The texts contain no decision IDs; many
do name their court or country in the header, as real uploads do.

Reports saved before this split hold the curated values under `inputs.gold`; `--baseline` still compares them,
but the per-theme tables need reports from the current harness.

## Scores

| Step | Score |
|---|---|
| jurisdiction | Alpha-3 code accuracy (the step also classifies the legal system, which is not curated) |
| col_section | How much of the curated excerpt is recovered, and output length relative to it |
| themes | Precision / recall / F1 against the curated themes |
| pil_provisions | Fuzzy precision / recall / F1 |
| case_citation | Normalized match |
| relevant_facts, col_issue, courts_position, abstract | Jev's probability that the answer agrees with the curated text |

Obiter dicta and dissenting opinions have no curated values and are not scored.
