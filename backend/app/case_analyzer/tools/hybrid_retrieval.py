"""Deterministic hybrid retrieval for choice-of-law candidate passages."""

from __future__ import annotations

from dataclasses import dataclass, field

import logfire

from .document_nav import DocumentContext, find_lexical_hits

RRF_OFFSET = 60
SEMANTIC_RESULTS_PER_QUERY = 4
LEXICAL_RESULTS_PER_QUERY = 3
DEFAULT_MAX_CANDIDATES = 18
DEFAULT_MAX_CANDIDATE_CHARS = 40_000
MAX_MERGED_PARAGRAPHS = 10

CHOICE_OF_LAW_CONCEPTS: tuple[tuple[str, str], ...] = (
    ("applicable_law", "the court determines the applicable, proper, or governing law"),
    ("applicable_law", "applicable law"),
    ("applicable_law", "governing law"),
    ("applicable_law", "proper law"),
    ("applicable_law", "choice of law"),
    ("party_autonomy", "party autonomy and an express or implied choice of law agreement"),
    ("party_autonomy", "choice of law clause"),
    ("conflict_rules", "conflict of laws rule or private international law rule used to select a law"),
    ("conflict_rules", "conflict of laws"),
    ("conflict_rules", "private international law"),
    ("connecting_factors", "closest connection, habitual residence, domicile, or characteristic performance"),
    ("foreign_law", "application, proof, interpretation, or exclusion of foreign law"),
    ("public_policy", "public policy exception to the otherwise applicable foreign law"),
    ("mandatory_rules", "overriding mandatory rules or lois de police affecting applicable law"),
    ("renvoi", "renvoi or reference to the conflict rules of another legal system"),
    ("clause_law", "law governing an arbitration agreement or jurisdiction clause"),
)


@dataclass(frozen=True)
class CandidatePassage:
    candidate_id: str
    start_paragraph: int
    end_paragraph: int
    text: str
    concepts: tuple[str, ...]
    retrieval_methods: tuple[str, ...]
    reciprocal_rank_score: float
    semantic_score: float | None = None

    @property
    def paragraph_numbers(self) -> tuple[int, ...]:
        return tuple(range(self.start_paragraph, self.end_paragraph + 1))


@dataclass(frozen=True)
class RetrievalResult:
    candidates: list[CandidatePassage]
    query_count: int
    semantic_available: bool
    semantic_unavailable_reason: str | None
    semantic_embedding_tokens: int
    semantic_chunk_count: int
    lexical_hit_count: int
    semantic_hit_count: int
    overlap_count: int


@dataclass
class _RankedRange:
    start: int
    end: int
    reciprocal_rank_score: float = 0.0
    semantic_score: float | None = None
    concepts: set[str] = field(default_factory=set)
    methods: set[str] = field(default_factory=set)


def _select_diverse_ranges(ranges: list[_RankedRange], concept_order: list[str], limit: int) -> list[_RankedRange]:
    ranked = sorted(ranges, key=lambda item: (-item.reciprocal_rank_score, item.start, item.end))
    selected: list[_RankedRange] = []
    selected_ids: set[int] = set()
    for concept in concept_order:
        match = next((item for item in ranked if concept in item.concepts and id(item) not in selected_ids), None)
        if match is not None:
            selected.append(match)
            selected_ids.add(id(match))
        if len(selected) == limit:
            return selected
    for item in ranked:
        if id(item) not in selected_ids:
            selected.append(item)
            selected_ids.add(id(item))
        if len(selected) == limit:
            break
    return selected


def _merge_ranges(ranges: list[_RankedRange], paragraph_count: int) -> list[_RankedRange]:
    expanded = [
        _RankedRange(
            start=max(1, item.start - 1),
            end=min(paragraph_count, item.end + 1),
            reciprocal_rank_score=item.reciprocal_rank_score,
            semantic_score=item.semantic_score,
            concepts=set(item.concepts),
            methods=set(item.methods),
        )
        for item in ranges
    ]
    merged: list[_RankedRange] = []
    for item in sorted(expanded, key=lambda value: (value.start, value.end)):
        if not merged:
            merged.append(item)
            continue
        previous = merged[-1]
        combined_end = max(previous.end, item.end)
        if item.start <= previous.end and combined_end - previous.start + 1 <= MAX_MERGED_PARAGRAPHS:
            previous.end = combined_end
            previous.reciprocal_rank_score += item.reciprocal_rank_score
            previous.semantic_score = max(
                (score for score in (previous.semantic_score, item.semantic_score) if score is not None),
                default=None,
            )
            previous.concepts.update(item.concepts)
            previous.methods.update(item.methods)
        else:
            merged.append(item)
    return merged


async def retrieve_choice_of_law_candidates(
    doc: DocumentContext,
    generated_queries: list[str] | None = None,
    *,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> RetrievalResult:
    """Retrieve, fuse, expand, and merge bounded choice-of-law candidates."""
    query_specs = list(CHOICE_OF_LAW_CONCEPTS)
    query_specs.extend(("case_specific", query) for query in generated_queries or [])
    deduped_specs: list[tuple[str, str]] = []
    seen_queries: set[str] = set()
    for concept, query in query_specs:
        normalized = " ".join(query.split())
        if normalized and normalized.casefold() not in seen_queries:
            seen_queries.add(normalized.casefold())
            deduped_specs.append((concept, normalized))

    with logfire.span("col_retrieval", query_count=len(deduped_specs), paragraph_count=len(doc.paragraphs)):
        semantic_by_query = await doc.semantic_search(
            [query for _concept, query in deduped_specs], top_k=SEMANTIC_RESULTS_PER_QUERY
        )
        aggregated: dict[tuple[int, int], _RankedRange] = {}
        lexical_ranges: set[tuple[int, int]] = set()
        semantic_ranges: set[tuple[int, int]] = set()
        lexical_hit_count = 0
        semantic_hit_count = 0

        for concept, query in deduped_specs:
            for rank, hit in enumerate(semantic_by_query.get(query, []), start=1):
                key = (hit.chunk.start_paragraph, hit.chunk.end_paragraph)
                item = aggregated.setdefault(key, _RankedRange(start=key[0], end=key[1]))
                item.reciprocal_rank_score += 1 / (RRF_OFFSET + rank)
                item.semantic_score = max(item.semantic_score or -1.0, hit.score)
                item.concepts.add(concept)
                item.methods.add("semantic")
                semantic_ranges.add(key)
                semantic_hit_count += 1

            for rank, hit in enumerate(find_lexical_hits(doc, query, max_results=LEXICAL_RESULTS_PER_QUERY), start=1):
                key = (hit.paragraph_number, hit.paragraph_number)
                item = aggregated.setdefault(key, _RankedRange(start=key[0], end=key[1]))
                item.reciprocal_rank_score += 1 / (RRF_OFFSET + rank)
                item.concepts.add(concept)
                item.methods.add(hit.method)
                lexical_ranges.add(key)
                lexical_hit_count += 1

        diverse = _select_diverse_ranges(
            list(aggregated.values()),
            [concept for concept, _query in deduped_specs],
            max_candidates * 2,
        )
        merged_by_relevance = sorted(
            _merge_ranges(diverse, len(doc.paragraphs)),
            key=lambda item: (-item.reciprocal_rank_score, item.start, item.end),
        )
        merged: list[_RankedRange] = []
        selected_chars = 0
        for item in merged_by_relevance:
            item_chars = sum(len(paragraph) for paragraph in doc.paragraphs[item.start - 1 : item.end])
            if merged and selected_chars + item_chars > DEFAULT_MAX_CANDIDATE_CHARS:
                continue
            merged.append(item)
            selected_chars += item_chars
            if len(merged) == max_candidates:
                break
        merged.sort(key=lambda item: (item.start, item.end))
        candidates = [
            CandidatePassage(
                candidate_id=f"C{index:03d}",
                start_paragraph=item.start,
                end_paragraph=item.end,
                text="\n\n".join(doc.paragraphs[item.start - 1 : item.end]),
                concepts=tuple(sorted(item.concepts)),
                retrieval_methods=tuple(sorted(item.methods)),
                reciprocal_rank_score=item.reciprocal_rank_score,
                semantic_score=item.semantic_score,
            )
            for index, item in enumerate(merged, start=1)
        ]

        index = doc._semantic_index
        semantic_available = bool(semantic_by_query) and doc.semantic_unavailable_reason is None
        overlap_count = len(lexical_ranges & semantic_ranges)
        logfire.info(
            "Choice-of-law candidates retrieved",
            candidate_count=len(candidates),
            lexical_hit_count=lexical_hit_count,
            semantic_hit_count=semantic_hit_count,
            lexical_semantic_overlap=overlap_count,
            semantic_available=semantic_available,
            lexical_fallback=not semantic_available,
            top_semantic_scores=sorted(
                (item.semantic_score for item in aggregated.values() if item.semantic_score is not None), reverse=True
            )[:5],
        )
        return RetrievalResult(
            candidates=candidates,
            query_count=len(deduped_specs),
            semantic_available=semantic_available,
            semantic_unavailable_reason=doc.semantic_unavailable_reason,
            semantic_embedding_tokens=index.embedding_tokens if index is not None else 0,
            semantic_chunk_count=len(index.chunks) if index is not None else 0,
            lexical_hit_count=lexical_hit_count,
            semantic_hit_count=semantic_hit_count,
            overlap_count=overlap_count,
        )
