"""Document navigation tools for case analyzer agents.

Provides content-anchored navigation over a court decision's markdown text.
No char-offset parameters — all tools use text anchors so agents don't drift.
"""

import re
import unicodedata
from dataclasses import dataclass, field

from agents import RunContextWrapper, Tool, function_tool
from rapidfuzz import fuzz

MAX_CHARS = 4000
_MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+.+")
_LINE_BREAK_HYPHEN_RE = re.compile(r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)")
_ALL_CAPS_HEADING_PUNCTUATION = frozenset(" -–—:;,.()[]/§0123456789")
_SEARCH_PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
    }
)


def _truncate(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + f"\n[truncated: {len(text) - MAX_CHARS} chars remaining]"


def _normalize_search_text(text: str) -> str:
    """Normalize multilingual and PDF-extracted text for matching only."""
    normalized = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    normalized = _LINE_BREAK_HYPHEN_RE.sub("", normalized)
    normalized = normalized.translate(_SEARCH_PUNCTUATION_TRANSLATION).casefold()
    normalized = "".join(
        character for character in unicodedata.normalize("NFKD", normalized) if unicodedata.category(character) != "Mn"
    )
    return " ".join(normalized.split())


def _detect_headings(paragraphs: list[str]) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for i, para in enumerate(paragraphs):
        first_line = para.strip().splitlines()[0] if para.strip() else ""
        letters = [character for character in first_line if character.isalpha()]
        is_all_caps_heading = (
            len(first_line) >= 5
            and bool(letters)
            and all(character.isupper() for character in letters)
            and all(character.isalpha() or character in _ALL_CAPS_HEADING_PUNCTUATION for character in first_line)
        )
        if _MARKDOWN_HEADING_RE.match(first_line) or is_all_caps_heading:
            result.append((first_line.strip(), i))
    return result


def _format_paragraph(paragraph_index: int, text: str) -> str:
    return f"[paragraph {paragraph_index + 1}]\n{text}"


@dataclass
class DocumentContext:
    draft_id: int
    text: str
    file_name: str | None = None
    paragraphs: list[str] = field(default_factory=list)
    headings: list[tuple[str, int]] = field(default_factory=list)
    normalized_paragraphs: list[str] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.paragraphs = [p for p in re.split(r"\n\s*\n", self.text) if p.strip()]
        self.headings = _detect_headings(self.paragraphs)
        self.normalized_paragraphs = [_normalize_search_text(paragraph) for paragraph in self.paragraphs]


@function_tool
def search(ctx: RunContextWrapper[DocumentContext], query: str, max_results: int = 5) -> str:
    """Search paragraphs for a query and return numbered matches for follow-up reading."""
    doc = ctx.context
    normalized_query = _normalize_search_text(query)
    if not normalized_query:
        return "[no matches]"

    indexed_paragraphs = list(enumerate(zip(doc.normalized_paragraphs, doc.paragraphs, strict=True)))
    hits = [(i, paragraph) for i, (normalized, paragraph) in indexed_paragraphs if normalized_query in normalized]
    if not hits and len(normalized_query) > 6:
        scored = sorted(
            (
                (fuzz.partial_ratio(normalized_query, normalized), i, paragraph)
                for i, (normalized, paragraph) in indexed_paragraphs
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        hits = [(i, paragraph) for score, i, paragraph in scored if score >= 80]
    hits = hits[:max_results]
    if not hits:
        return "[no matches]"
    return _truncate("\n---\n".join(_format_paragraph(i, paragraph) for i, paragraph in hits))


@function_tool
def get_paragraph_containing(ctx: RunContextWrapper[DocumentContext], text_snippet: str) -> str:
    """Return the full paragraph that contains the given text snippet (case-insensitive)."""
    doc = ctx.context
    needle = _normalize_search_text(text_snippet)
    if not needle:
        return "[not found]"
    for i, (normalized, para) in enumerate(zip(doc.normalized_paragraphs, doc.paragraphs, strict=True)):
        if needle in normalized:
            return _truncate(_format_paragraph(i, para))
    return "[not found]"


@function_tool
def read_paragraphs(
    ctx: RunContextWrapper[DocumentContext],
    start_paragraph: int,
    count: int = 5,
) -> str:
    """Read up to 10 paragraphs from a 1-based paragraph number returned by search."""
    paragraphs = ctx.context.paragraphs
    start_index = start_paragraph - 1
    if start_index < 0 or start_index >= len(paragraphs):
        return "[paragraph out of range]"
    end_index = min(len(paragraphs), start_index + max(1, min(count, 10)))
    return _truncate("\n\n".join(_format_paragraph(i, paragraphs[i]) for i in range(start_index, end_index)))


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
    needle = _normalize_search_text(heading)
    if not needle:
        return "[heading not found]"
    start_idx: int | None = None
    for h, para_idx in doc.headings:
        if needle in _normalize_search_text(h):
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
    match = re.search(re.escape(anchor), text, re.IGNORECASE)
    if match is None:
        return "[anchor not found]"
    start = max(0, match.start() - max(0, chars_before))
    end = min(len(text), match.end() + max(0, chars_after))
    return _truncate(text[start:end])


@function_tool
def read_head(ctx: RunContextWrapper[DocumentContext], n_chars: int = 2000) -> str:
    """Return the first n_chars of the document (useful for case citation, parties, docket)."""
    return _truncate(ctx.context.text[: max(1, n_chars)])


@function_tool
def read_tail(ctx: RunContextWrapper[DocumentContext], n_chars: int = 2000) -> str:
    """Return the last n_chars of the document (useful for signatures, dates, dissents)."""
    return _truncate(ctx.context.text[-max(1, n_chars) :])


NAV_TOOLS: list[Tool] = [
    search,
    get_paragraph_containing,
    read_paragraphs,
    list_headings,
    read_section,
    read_window,
    read_head,
    read_tail,
]
