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

from .semantic_index import CHUNK_MAX_CHARS, EmbedFunction, SemanticHit, SemanticIndex

logger = logging.getLogger(__name__)

MAX_CHARS = 4000
MAX_PARAGRAPH_CHARS = CHUNK_MAX_CHARS
MIN_PARAGRAPH_CHARS = 200
MAX_FURNITURE_CHARS = 150
MIN_FURNITURE_REPEATS = 3
_BLOCK_SEPARATOR_RE = re.compile(r"\n[ \t]*\n")
_PAGE_MARKER_RE = re.compile(
    r"^(?:[-–—]\s*\d{1,4}\s*[-–—]"
    r"|(?:page|p\.|pág\.?|página|seite|pagina)\s*\d{1,4}(?:\s*(?:/|of|de|von|di)\s*\d{1,4})?"
    r"|\d{1,4}\s*(?:/|of|de|von)\s*\d{1,4}"
    r"|(?:\.\s*){3,}\d{1,4})$",
    re.I,
)
_BARE_NUMBER_RE = re.compile(r"^\d{1,4}\.?$")
FURNITURE_MIN_SPREAD = 0.25
MIN_FURNITURE_LETTERS = 8
_NUMBERED_BLOCK_RE = re.compile(r"^[-–—>#*\s\[]*(?:note:?\s*)?\d", re.I)
_EMPHASIS_RE = re.compile(r"(?<![\w*])(?:\*{1,3}|_{1,2})(?=\S)|(?<=\S)(?:\*{1,3}|_{1,2})(?![\w*])")
_SUPERSCRIPT_RE = re.compile(r"<sup>\s*([0-9]+)\s*</sup>", re.I)
_HTML_TAG_RE = re.compile(r"</?(?:sup|sub|u|b|i|em|strong|span|br|mark)\b[^>]*>", re.I)
_PICTURE_TEXT_RE = re.compile(r"<!--\s*Start of picture text\s*-->(.*?)<!--\s*End of picture text\s*-->", re.S)
_SPACE_BEFORE_PUNCTUATION_RE = re.compile(r"(?<=\w) +(?=[,;])")
FURNITURE_SIMILARITY = 85
_SUPERSCRIPT_DIGITS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_SENTENCE_END = tuple(".:;?!)]}\"'»”’…")
_PARAGRAPH_SEPARATORS = (re.compile(r"\n"), re.compile(r"(?<=[.!?])\s+"), re.compile(r"\s+"))
_PARAGRAPH_JOINERS = ("\n", " ", " ")
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


def _heading_line(paragraph: str) -> str | None:
    """The paragraph's first line when it is a markdown or all-caps heading."""
    first_line = paragraph.strip().splitlines()[0] if paragraph.strip() else ""
    letters = [character for character in first_line if character.isalpha()]
    is_all_caps_heading = (
        len(first_line) >= 5
        and bool(letters)
        and all(character.isupper() for character in letters)
        and all(character.isalpha() or character in _ALL_CAPS_HEADING_PUNCTUATION for character in first_line)
    )
    return first_line.strip() if _MARKDOWN_HEADING_RE.match(first_line) or is_all_caps_heading else None


def _detect_headings(paragraphs: list[str]) -> list[tuple[str, int]]:
    return [(heading, i) for i, para in enumerate(paragraphs) if (heading := _heading_line(para)) is not None]


def merge_fragments(paragraphs: list[str], min_chars: int = MIN_PARAGRAPH_CHARS) -> list[str]:
    """Prepend paragraphs shorter than min_chars (headings, page numbers, stray lines) to the paragraph after them.

    A heading always starts the paragraph it is merged into, so heading detection still finds it; nothing is merged
    past MAX_PARAGRAPH_CHARS, and trailing fragments join the paragraph before them.
    """
    merged: list[str] = []
    pending: list[str] = []
    for paragraph in paragraphs:
        if pending and (_heading_line(paragraph) is not None or len("\n\n".join([*pending, paragraph])) > MAX_PARAGRAPH_CHARS):
            merged.append("\n\n".join(pending))
            pending = []
        if len(paragraph) < min_chars:
            pending.append(paragraph)
            continue
        merged.append("\n\n".join([*pending, paragraph]))
        pending = []
    if pending:
        tail = "\n\n".join(pending)
        if merged and _heading_line(tail) is None and len(merged[-1]) + 2 + len(tail) <= MAX_PARAGRAPH_CHARS:
            merged[-1] = f"{merged[-1]}\n\n{tail}"
        else:
            merged.append(tail)
    return merged


def _format_paragraph(paragraph_index: int, text: str) -> str:
    return f"[paragraph {paragraph_index + 1}]\n{text}"


@dataclass(frozen=True)
class LexicalHit:
    paragraph_number: int
    text: str
    score: float
    method: str


def _furniture_key(block: str) -> str:
    return re.sub(r"\d+", "#", " ".join(block.split()).casefold())


def _picture_text(match: re.Match[str]) -> str:
    """OCR text found inside an image: logos and seals are short noise, a scanned page is the decision itself."""
    inner = match.group(1).strip()
    return inner if len(inner) > MAX_FURNITURE_CHARS else ""


def _strip_emphasis(line: str) -> str:
    """Remove markdown emphasis markers, repeating for nested ones such as **_1-_**."""
    while (stripped := _EMPHASIS_RE.sub("", line)) != line:
        line = stripped
    return line


def _strip_inline_markup(text: str) -> str:
    text = _PICTURE_TEXT_RE.sub(_picture_text, text)
    text = _SUPERSCRIPT_RE.sub(lambda match: match.group(1).translate(_SUPERSCRIPT_DIGITS), text)
    text = _HTML_TAG_RE.sub("", text)
    lines = (line if line.lstrip().startswith("#") else _strip_emphasis(line) for line in text.split("\n"))
    return _SPACE_BEFORE_PUNCTUATION_RE.sub("", "\n".join(lines))


def _continues(previous: str, block: str) -> bool:
    """Whether block continues the sentence previous was cut off in, as at a page break."""
    first = block.lstrip()[:1]
    return (
        bool(first)
        and first.islower()
        and not block.lstrip().startswith(("http", "www."))
        and not previous.rstrip().endswith(_SENTENCE_END)
        and _heading_line(previous) is None
    )


def _is_sentence(block: str) -> bool:
    """A full sentence, such as one a court quotes several times, rather than a header."""
    return block.rstrip().endswith((".", ";")) and len(block.split()) >= 6


def _furniture_keys(blocks: list[str]) -> set[str]:
    """Running headers and footers: short blocks with at least MIN_FURNITURE_LETTERS letters, repeated
    MIN_FURNITURE_REPEATS times or more across at least FURNITURE_MIN_SPREAD of the document, digits ignored.

    The spread rule spares repeated table cells. The letter rule and skipping blocks that start with a number spare
    footnotes and numbered paragraph headings, which look alike once their digits are ignored; full sentences a court
    quotes more than once are spared too."""
    positions: dict[str, list[int]] = {}
    for index, block in enumerate(blocks):
        if (
            len(block) <= MAX_FURNITURE_CHARS
            and sum(character.isalpha() for character in block) >= MIN_FURNITURE_LETTERS
            and not _NUMBERED_BLOCK_RE.match(block)
            and not _is_sentence(block)
        ):
            positions.setdefault(_furniture_key(block), []).append(index)
    span = FURNITURE_MIN_SPREAD * len(blocks)
    return {key for key, found in positions.items() if len(found) >= MIN_FURNITURE_REPEATS and found[-1] - found[0] >= span}


def clean_document_text(text: str) -> str:
    """Remove PDF page furniture and rejoin sentences that a page break split.

    Running headers and footers (see _furniture_keys) keep only their first occurrence, so an identifier printed in
    every header is still there once; short blocks that nearly match one (an OCR-garbled copy) go too. Page markers
    such as "- 2 -", "Page 4" or "3/12" go; a bare number goes only inside a sentence a page break split, since it is
    otherwise often a paragraph number. Short OCR'd picture text (logos, seals), inline markdown emphasis and HTML tags
    are removed (footnote markers become superscript digits), and a block that ends mid-sentence is joined with the
    next when it continues in lowercase.
    """
    blocks = [block.strip() for block in _BLOCK_SEPARATOR_RE.split(_strip_inline_markup(text)) if block.strip()]
    furniture = _furniture_keys(blocks)
    seen: set[str] = set()
    content: list[str] = []
    for block in blocks:
        if _PAGE_MARKER_RE.match(block.lstrip("# ")):
            continue
        if len(block) <= MAX_FURNITURE_CHARS:
            key = _furniture_key(block)
            if key in furniture:
                if key in seen:
                    continue
                seen.add(key)
            elif any(fuzz.ratio(key, header) >= FURNITURE_SIMILARITY for header in furniture):
                continue
        content.append(block)

    kept: list[str] = []
    for index, block in enumerate(content):
        following = content[index + 1] if index + 1 < len(content) else ""
        if _BARE_NUMBER_RE.match(block) and kept and _continues(kept[-1], following):
            continue
        if kept and _continues(kept[-1], block):
            kept[-1] = f"{kept[-1]} {block}"
        else:
            kept.append(block)
    return "\n\n".join(kept)


def split_oversized_paragraph(text: str, max_chars: int = MAX_PARAGRAPH_CHARS, level: int = 0) -> list[str]:
    """Split text longer than max_chars at line breaks, then sentence ends, then spaces, packing pieces greedily.

    Extracted text without blank lines otherwise becomes one paragraph the size of the document, which no
    embedding request, Jev question or paragraph-level selection can handle.
    """
    if len(text) <= max_chars:
        return [text]
    if level == len(_PARAGRAPH_SEPARATORS):
        return [text[start : start + max_chars] for start in range(0, len(text), max_chars)]
    pieces = [piece for piece in _PARAGRAPH_SEPARATORS[level].split(text) if piece.strip()]
    if len(pieces) == 1:
        return split_oversized_paragraph(text, max_chars, level + 1)
    joiner = _PARAGRAPH_JOINERS[level]
    packed: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + len(joiner) + len(piece) > max_chars:
            packed.append(current)
            current = piece
        else:
            current = f"{current}{joiner}{piece}" if current else piece
    packed.append(current)
    return [part for chunk in packed for part in split_oversized_paragraph(chunk, max_chars, level + 1)]


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
        self.text = clean_document_text(self.text)
        self.paragraphs = merge_fragments(
            [part for p in re.split(r"\n\s*\n", self.text) if p.strip() for part in split_oversized_paragraph(p)]
        )
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
