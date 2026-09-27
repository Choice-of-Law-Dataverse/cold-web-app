"""Build a frozen evaluation corpus of curated court decisions.

Each entry holds a decision's full text and the curated value for every analyzer step, taken
from the public CoLD API. Entries are split deterministically into a small dev set for
iteration and a held-out test set for model decisions.

    uv run python -m evals.corpus --dev-size 30
"""

import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, get_args

import httpx2

from app.case_analyzer.tools.models import Theme

EVAL_DIR = Path("analyzer-eval")
CORPUS_DIR = EVAL_DIR / "corpus"
PLACEHOLDERS = {"na", "n/a", "not found", "none", "-"}

THEME_ALIASES: dict[str, Theme] = {"overriding mandatory rules": "Mandatory rules"}
THEME_BY_KEY: dict[str, Theme] = dict(THEME_ALIASES)
for _theme in get_args(Theme):
    THEME_BY_KEY[_theme.casefold()] = _theme


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def field(record: dict[str, Any], name: str) -> str:
    value = record.get(name)
    if isinstance(value, str) and value.strip() and value.strip().casefold() not in PLACEHOLDERS:
        return value.strip()
    return ""


def split_list(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[|;\n]", value) if part.strip()]


def curated_themes(value: str) -> list[Theme]:
    themes: set[Theme] = set()
    for name in split_list(value):
        if theme := THEME_BY_KEY.get(name.casefold()):
            themes.add(theme)
    return sorted(themes)


def to_entry(record: dict[str, Any]) -> dict[str, Any] | None:
    """A corpus entry, or None when the decision has no full text or no curated CoL analysis."""
    text_source = next((name for name in ("originaltext", "englishtranslation") if field(record, name)), None)
    if text_source is None or not (field(record, "quote") or field(record, "choiceoflawissue")):
        return None
    jurisdictions = record.get("jurisdictions")
    return {
        "id": record.get("id"),
        "text": field(record, text_source),
        "text_source": text_source,
        "added_by": record.get("addedbyemail") or record.get("createdbyemail"),
        "gold": {
            "jurisdiction_code": field(record, "jurisdictionsalpha3code"),
            "jurisdiction": jurisdictions if isinstance(jurisdictions, str) else "",
            "col_excerpt": field(record, "quote") or field(record, "translatedexcerpt"),
            "themes": curated_themes(field(record, "themes")),
            "case_citation": field(record, "casecitation"),
            "pil_provisions": split_list(field(record, "pilprovisions")),
            "relevant_facts": field(record, "relevantfacts"),
            "col_issue": field(record, "choiceoflawissue"),
            "courts_position": field(record, "courtsposition"),
            "abstract": field(record, "abstract"),
        },
    }


def _split_rank(entry_id: str) -> str:
    return hashlib.sha256(entry_id.encode()).hexdigest()


async def fetch_court_decisions(api_base: str) -> list[dict[str, Any]]:
    async with httpx2.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{api_base}/api/v1/search/full_table", params={"table": "Court Decisions"})
        response.raise_for_status()
        return [{_key(name): value for name, value in record.items()} for record in response.json()]


def load(split: str) -> list[dict[str, Any]]:
    path = CORPUS_DIR / f"{split}.jsonl"
    if not path.exists():
        raise SystemExit(f"{path} not found; build it first with: uv run python -m evals.corpus")
    return [json.loads(line) for line in path.read_text().splitlines()]


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api-base", default="https://api.cold.global")
    parser.add_argument("--dev-size", type=int, default=30)
    args = parser.parse_args()

    records = await fetch_court_decisions(args.api_base)
    entries = sorted(
        (entry for record in records if (entry := to_entry(record)) and entry["id"]),
        key=lambda entry: _split_rank(str(entry["id"])),
    )
    splits = {"dev": entries[: args.dev_size], "test": entries[args.dev_size :]}

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        (CORPUS_DIR / f"{name}.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in split))

    print(f"{len(records)} court decisions; {len(entries)} have full text and curated CoL analysis.")
    for name, split in splits.items():
        coverage = {key: sum(1 for e in split if e["gold"][key]) for key in split[0]["gold"]} if split else {}
        print(f"{name}: {len(split)} decisions; curated values per step: {coverage}")


if __name__ == "__main__":
    asyncio.run(main())
