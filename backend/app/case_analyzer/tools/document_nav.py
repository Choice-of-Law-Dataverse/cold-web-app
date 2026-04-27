"""Document navigation tools for case analyzer agents.

Provides content-anchored navigation over a court decision's markdown text.
No char-offset parameters — all tools use text anchors so agents don't drift.
"""

import re
from dataclasses import dataclass, field

from agents import RunContextWrapper, function_tool
from rapidfuzz import fuzz

MAX_CHARS = 4000
_HEADING_RE = re.compile(r"^(#{1,6}\s+.+|[A-Z][A-Z\s\-]{4,}$)")


def _truncate(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + f"\n[truncated: {len(text) - MAX_CHARS} chars remaining]"


def _detect_headings(paragraphs: list[str]) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for i, para in enumerate(paragraphs):
        first_line = para.strip().splitlines()[0] if para.strip() else ""
        if _HEADING_RE.match(first_line):
            result.append((first_line.strip(), i))
    return result


@dataclass
class DocumentContext:
    draft_id: int
    text: str
    paragraphs: list[str] = field(default_factory=list)
    headings: list[tuple[str, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.paragraphs = [p for p in re.split(r"\n\s*\n", self.text) if p.strip()]
        self.headings = _detect_headings(self.paragraphs)


@function_tool
def search(ctx: RunContextWrapper[DocumentContext], query: str, max_results: int = 5) -> str:
    """Search for paragraphs containing the query string. Returns up to max_results matches."""
    doc = ctx.context
    hits = [p for p in doc.paragraphs if query.lower() in p.lower()]
    if not hits and len(query) > 6:
        scored = sorted(
            ((fuzz.partial_ratio(query.lower(), p.lower()), p) for p in doc.paragraphs),
            reverse=True,
        )
        hits = [p for score, p in scored if score >= 80]
    hits = hits[:max_results]
    if not hits:
        return "[no matches]"
    return _truncate("\n---\n".join(hits))


@function_tool
def get_paragraph_containing(ctx: RunContextWrapper[DocumentContext], text_snippet: str) -> str:
    """Return the full paragraph that contains the given text snippet (case-insensitive)."""
    doc = ctx.context
    needle = text_snippet.lower()
    for para in doc.paragraphs:
        if needle in para.lower():
            return _truncate(para)
    return "[not found]"


@function_tool
def list_headings(ctx: RunContextWrapper[DocumentContext]) -> str:
    """List detected section headings in document order."""
    headings = ctx.context.headings
    if not headings:
        return "[no headings detected]"
    return "\n".join(f"{i + 1}. {h}" for i, (h, _) in enumerate(headings))


@function_tool
def read_section(ctx: RunContextWrapper[DocumentContext], heading: str) -> str:
    """Return text from the named heading until the next heading (case-insensitive match)."""
    doc = ctx.context
    needle = heading.lower()
    start_idx: int | None = None
    for h, para_idx in doc.headings:
        if needle in h.lower():
            start_idx = para_idx
            break
    if start_idx is None:
        return "[heading not found]"
    end_idx = len(doc.paragraphs)
    for _h, para_idx in doc.headings:
        if para_idx > start_idx:
            end_idx = para_idx
            break
    section = "\n\n".join(doc.paragraphs[start_idx:end_idx])
    return _truncate(section)


@function_tool
def read_window(
    ctx: RunContextWrapper[DocumentContext],
    anchor: str,
    chars_before: int = 500,
    chars_after: int = 2000,
) -> str:
    """Return text surrounding the first occurrence of anchor (case-insensitive)."""
    text = ctx.context.text
    needle_pos = text.lower().find(anchor.lower())
    if needle_pos == -1:
        return "[anchor not found]"
    start = max(0, needle_pos - chars_before)
    end = min(len(text), needle_pos + len(anchor) + chars_after)
    window = text[start:end]
    return _truncate(window)


@function_tool
def read_head(ctx: RunContextWrapper[DocumentContext], n_chars: int = 2000) -> str:
    """Return the first n_chars of the document (useful for case citation, parties, docket)."""
    return _truncate(ctx.context.text[:n_chars])


@function_tool
def read_tail(ctx: RunContextWrapper[DocumentContext], n_chars: int = 2000) -> str:
    """Return the last n_chars of the document (useful for signatures, dates, dissents)."""
    return _truncate(ctx.context.text[-n_chars:])
