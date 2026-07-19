"""Document navigation tools for case analyzer agents.

Provides content-anchored navigation over a court decision's markdown text.
No char-offset parameters — all tools use text anchors so agents don't drift.
"""

import asyncio
import logging
import re
import unicodedata
from dataclasses import dataclass, field

from agents import RunContextWrapper, Tool, function_tool
from rapidfuzz import fuzz

from .semantic_index import EmbedFunction, SemanticHit, SemanticIndex

logger = logging.getLogger(__name__)

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


@dataclass(frozen=True)
class LexicalHit:
    paragraph_number: int
    text: str
    score: float
    method: str


@dataclass
class DocumentContext:
    draft_id: int
    text: str
    file_name: str | None = None
    paragraphs: list[str] = field(default_factory=list)
    headings: list[tuple[str, int]] = field(default_factory=list)
    normalized_paragraphs: list[str] = field(default_factory=list, repr=False)
    semantic_embedder: EmbedFunction | None = field(default=None, repr=False)
    _semantic_index: SemanticIndex | None = field(default=None, init=False, repr=False)
    _semantic_build_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _semantic_build_task: asyncio.Task[SemanticIndex] | None = field(default=None, init=False, repr=False)
    _semantic_query_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _semantic_query_cache: dict[str, list[float]] = field(default_factory=dict, init=False, repr=False)
    semantic_unavailable_reason: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.paragraphs = [p for p in re.split(r"\n\s*\n", self.text) if p.strip()]
        self.headings = _detect_headings(self.paragraphs)
        self.normalized_paragraphs = [_normalize_search_text(paragraph) for paragraph in self.paragraphs]

    async def get_semantic_index(self) -> SemanticIndex | None:
        """Build the request-scoped index once, sharing concurrent callers."""
        if self._semantic_index is not None:
            return self._semantic_index
        if self.semantic_unavailable_reason is not None:
            return None

        async with self._semantic_build_lock:
            if self._semantic_build_task is None:
                index = SemanticIndex(self.paragraphs, embed=self.semantic_embedder)
                self._semantic_build_task = asyncio.create_task(self._build_semantic_index(index))
            task = self._semantic_build_task

        try:
            self._semantic_index = await task
        except Exception as exc:
            self.semantic_unavailable_reason = type(exc).__name__
            logger.warning("Semantic retrieval unavailable for draft %d: %s", self.draft_id, type(exc).__name__)
            return None
        return self._semantic_index

    async def _build_semantic_index(self, index: SemanticIndex) -> SemanticIndex:
        await index.build()
        return index

    async def semantic_search(self, queries: list[str], *, top_k: int = 4) -> dict[str, list[SemanticHit]]:
        """Rank chunks for multiple queries with a per-document embedding cache."""
        index = await self.get_semantic_index()
        if index is None:
            return {}

        normalized_queries = list(dict.fromkeys(" ".join(query.split()) for query in queries if query.strip()))
        try:
            async with self._semantic_query_lock:
                missing = [query for query in normalized_queries if query.casefold() not in self._semantic_query_cache]
                if missing:
                    response = await index.embed_queries(missing)
                    if len(response.vectors) != len(missing):
                        raise ValueError("Embedding response count did not match query count")
                    for query, vector in zip(missing, response.vectors, strict=True):
                        self._semantic_query_cache[query.casefold()] = vector
        except Exception as exc:
            self.semantic_unavailable_reason = type(exc).__name__
            logger.warning("Semantic query embedding unavailable for draft %d: %s", self.draft_id, type(exc).__name__)
            return {}

        return {
            query: index.rank(query, self._semantic_query_cache[query.casefold()], top_k=top_k) for query in normalized_queries
        }


def find_lexical_hits(doc: DocumentContext, query: str, *, max_results: int = 5) -> list[LexicalHit]:
    """Return structured exact or fuzzy paragraph hits without changing source text."""
    normalized_query = _normalize_search_text(query)
    if not normalized_query:
        return []

    exact_hits = [
        LexicalHit(
            paragraph_number=index + 1,
            text=paragraph,
            score=1.0,
            method="heading" if any(heading_index == index for _heading, heading_index in doc.headings) else "exact",
        )
        for index, (normalized, paragraph) in enumerate(zip(doc.normalized_paragraphs, doc.paragraphs, strict=True))
        if normalized_query in normalized
    ]
    if exact_hits:
        return exact_hits[:max_results]
    if len(normalized_query) <= 6:
        return []

    scored = sorted(
        (
            (fuzz.partial_ratio(normalized_query, normalized), index, paragraph)
            for index, (normalized, paragraph) in enumerate(zip(doc.normalized_paragraphs, doc.paragraphs, strict=True))
        ),
        key=lambda item: (-item[0], item[1]),
    )
    return [
        LexicalHit(paragraph_number=index + 1, text=paragraph, score=score / 100, method="fuzzy")
        for score, index, paragraph in scored
        if score >= 80
    ][:max_results]


@function_tool
def search(ctx: RunContextWrapper[DocumentContext], query: str, max_results: int = 5) -> str:
    """Search paragraphs for a query and return numbered matches for follow-up reading."""
    hits = find_lexical_hits(ctx.context, query, max_results=max_results)
    if not hits:
        return "[no matches]"
    return _truncate("\n---\n".join(_format_paragraph(hit.paragraph_number - 1, hit.text) for hit in hits))


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
