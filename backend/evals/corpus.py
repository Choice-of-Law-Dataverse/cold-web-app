"""Build a frozen evaluation corpus of curated court decisions.

Each entry holds a decision's full text and the curated value for every analyzer step, taken
from the public CoLD API. Decisions without Original_Text or an English translation can use
the text extracted from their official PDF (scripts/extract_court_decision_texts.py). Each
decision is assigned to the dev set (iteration) or the held-out test set (model decisions) by
a hash of its ID, so adding decisions never moves an existing one between sets.

    uv run python scripts/extract_court_decision_texts.py --out analyzer-eval/texts.jsonl
    uv run python -m evals.corpus --texts analyzer-eval/texts.jsonl
"""

import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, get_args

import httpx2

from app.case_analyzer.tools.jurisdiction_classifier import jurisdiction_codes
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


def curated_jurisdiction_codes(record: dict[str, Any]) -> list[str]:
    """Every curated jurisdiction's Alpha-3 code; the API's code field holds only the first of several."""
    by_name = {name.casefold(): code for name, code in jurisdiction_codes().items()}
    jurisdictions = record.get("jurisdictions")
    names = split_list(jurisdictions) if isinstance(jurisdictions, str) else []
    codes = [field(record, "jurisdictionsalpha3code").upper()] + [by_name.get(name.casefold(), "") for name in names]
    return sorted({code for code in codes if code})


def text_and_excerpt(record: dict[str, Any], pdf_text: str = "") -> tuple[str | None, str, str]:
    """The full text's source, the full text and the curated CoL excerpt, in the same language where possible.

    The curated quote is in the decision's original language and the translated excerpt in English, so the scorer's
    fuzzy comparison only means something when the text is in the excerpt's language. Original_Text pairs with the
    quote; the English translation pairs with the translated excerpt; when the only excerpt is the quote, the PDF
    text (the original) is taken over the English translation. Otherwise the first available text and excerpt.
    """
    texts = {"originaltext": field(record, "originaltext"), "englishtranslation": field(record, "englishtranslation")}
    texts["pdf"] = pdf_text.strip()
    quote, translated = field(record, "quote"), field(record, "translatedexcerpt")
    if texts["originaltext"]:
        return "originaltext", texts["originaltext"], quote or translated
    if texts["englishtranslation"] and translated:
        return "englishtranslation", texts["englishtranslation"], translated
    if texts["pdf"] and quote:
        return "pdf", texts["pdf"], quote
    text_source = next((name for name, text in texts.items() if text), None)
    return text_source, texts[text_source] if text_source else "", quote or translated


def to_entry(record: dict[str, Any], pdf_text: str = "") -> dict[str, Any] | None:
    """A corpus entry, or None when the decision has no full text or no curated value at all.

    Each step only runs on the entries that have its curated values, so an entry with just a
    curated jurisdiction still counts towards the jurisdiction step. See text_and_excerpt for which text is used.
    """
    text_source, text, col_excerpt = text_and_excerpt(record, pdf_text)
    if text_source is None:
        return None
    jurisdictions = record.get("jurisdictions")
    gold: dict[str, Any] = {
        "jurisdiction_code": field(record, "jurisdictionsalpha3code"),
        "jurisdiction_codes": curated_jurisdiction_codes(record),
        "jurisdiction": jurisdictions if isinstance(jurisdictions, str) else "",
        "col_excerpt": col_excerpt,
        "themes": curated_themes(field(record, "themes")),
        "case_citation": field(record, "casecitation"),
        "pil_provisions": split_list(field(record, "pilprovisions")),
        "relevant_facts": field(record, "relevantfacts"),
        "col_issue": field(record, "choiceoflawissue"),
        "courts_position": field(record, "courtsposition"),
        "abstract": field(record, "abstract"),
    }
    if not any(gold.values()):
        return None
    return {
        "id": record.get("id"),
        "text": text,
        "text_source": text_source,
        "added_by": record.get("addedbyemail") or record.get("createdbyemail"),
        "gold": gold,
    }


def split_of(entry_id: str, dev_share: float) -> str:
    bucket = int(hashlib.sha256(entry_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "dev" if bucket < dev_share else "test"


def load_pdf_texts(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    rows = (json.loads(line) for line in path.read_text().splitlines())
    return {row["id"]: row["text"] for row in rows if row.get("text")}


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
    parser.add_argument("--dev-share", type=float, default=0.5, help="Share of decisions in the dev set")
    parser.add_argument("--texts", type=Path, default=None, help="JSONL from extract_court_decision_texts.py")
    args = parser.parse_args()

    records = await fetch_court_decisions(args.api_base)
    pdf_texts = load_pdf_texts(args.texts)
    entries = sorted(
        (entry for record in records if (entry := to_entry(record, pdf_texts.get(str(record.get("id")), ""))) and entry["id"]),
        key=lambda entry: str(entry["id"]),
    )
    splits: dict[str, list[dict[str, Any]]] = {"dev": [], "test": []}
    for entry in entries:
        splits[split_of(str(entry["id"]), args.dev_share)].append(entry)

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        (CORPUS_DIR / f"{name}.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in split))

    sources = {
        name: sum(1 for e in entries if e["text_source"] == name) for name in ("originaltext", "englishtranslation", "pdf")
    }
    print(f"{len(records)} court decisions; {len(entries)} have full text and a curated value. Text from: {sources}")
    for name, split in splits.items():
        coverage = {key: sum(1 for e in split if e["gold"][key]) for key in split[0]["gold"]} if split else {}
        print(f"{name}: {len(split)} decisions; curated values per step: {coverage}")


if __name__ == "__main__":
    asyncio.run(main())
