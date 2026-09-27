"""Extract court decision text from the official source PDFs.

Downloads every court decision's official PDF from the public CoLD API data and extracts its
text with the case analyzer's PDF handler. Writes one JSON line per decision to --out:
{"id", "pdf_url", "chars", "text", "error"}. It never writes to the database; backfilling
Original_Text from this file is a separate, reviewed step.

    uv run python scripts/extract_court_decision_texts.py --out jev-eval/texts.jsonl
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import httpx2
from jev_eval import fetch_corpus

from app.case_analyzer.utils.pdf_handler import extract_text_from_pdf

MAX_PDF_BYTES = 50 * 1024 * 1024


def pdf_url(value: Any) -> str | None:
    """The PDF link from a plain URL or a NocoDB attachment object/list."""
    if isinstance(value, list):
        return next((url for item in value if (url := pdf_url(item))), None)
    if isinstance(value, dict):
        for key in ("signedUrl", "url"):
            if isinstance(value.get(key), str):
                return pdf_url(value[key])
        return None
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("["):
            try:
                return pdf_url(json.loads(value))
            except json.JSONDecodeError:
                return None
        return value if value.startswith("http") else None
    return None


async def extract(client: httpx2.AsyncClient, record: dict[str, Any]) -> dict[str, Any]:
    url = pdf_url(record.get("officialsourcepdf"))
    row: dict[str, Any] = {"id": record.get("id"), "pdf_url": url, "chars": 0, "text": "", "error": None}
    if url is None:
        row["error"] = "no PDF URL"
        return row
    try:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content
        if len(content) > MAX_PDF_BYTES:
            row["error"] = f"PDF larger than {MAX_PDF_BYTES // (1024 * 1024)} MB"
        elif not content.startswith(b"%PDF"):
            row["error"] = f"not a PDF ({response.headers.get('content-type', 'unknown type')})"
        else:
            text = await asyncio.to_thread(extract_text_from_pdf, content)
            row.update(text=text, chars=len(text), error=None if text.strip() else "no extractable text (scanned?)")
    except (httpx2.HTTPError, ValueError) as e:
        row["error"] = str(e)[:300]
    return row


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api-base", default="https://api.cold.global")
    parser.add_argument("--out", type=Path, default=Path("jev-eval/texts.jsonl"))
    parser.add_argument("--limit", type=int, default=None, help="Extract at most this many PDFs")
    parser.add_argument("--concurrency", type=int, default=6)
    args = parser.parse_args()

    corpus = await fetch_corpus(args.api_base)
    records = [r for r in corpus if r.get("officialsourcepdf")]
    records = records[: args.limit] if args.limit else records

    semaphore = asyncio.Semaphore(args.concurrency)
    async with httpx2.AsyncClient(timeout=120.0, follow_redirects=True) as client:

        async def run(record: dict[str, Any]) -> dict[str, Any]:
            async with semaphore:
                return await extract(client, record)

        rows = await asyncio.gather(*(run(r) for r in records))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))

    extracted = [r for r in rows if not r["error"]]
    errors: dict[str, int] = {}
    for row in rows:
        if row["error"]:
            kind = row["error"].split(":")[0][:80]
            errors[kind] = errors.get(kind, 0) + 1
    lines = [
        "## PDF text extraction",
        "",
        f"{len(corpus)} court decisions; {len(records)} link a PDF; text extracted from {len(extracted)}.",
    ]
    if extracted:
        sizes = sorted(r["chars"] for r in extracted)
        lines.append(f"Extracted length: median {sizes[len(sizes) // 2]:,} characters.")
    if errors:
        lines += ["", "| Failure | Count |", "|---|---|"]
        lines += [f"| {kind} | {count} |" for kind, count in sorted(errors.items(), key=lambda item: -item[1])]
    report = "\n".join(lines) + "\n"
    args.out.with_name("extraction.md").write_text(report)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
