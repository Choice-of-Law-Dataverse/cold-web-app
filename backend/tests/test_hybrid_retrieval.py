"""Tests for deterministic lexical and semantic candidate retrieval."""

import pytest

from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.hybrid_retrieval import retrieve_choice_of_law_candidates
from app.case_analyzer.tools.semantic_index import EmbeddingBatch


def _concept_vector(text: str) -> list[float]:
    normalized = text.casefold()
    legal_terms = (
        "law",
        "loi",
        "recht",
        "conflit",
        "governing",
        "applicable",
        "party autonomy",
        "connecting",
        "foreign",
        "public policy",
        "mandatory",
        "renvoi",
        "clause",
    )
    return [1.0, 0.0] if any(term in normalized for term in legal_terms) else [0.0, 1.0]


async def _embed(texts: list[str]) -> EmbeddingBatch:
    return EmbeddingBatch(vectors=[_concept_vector(text) for text in texts], token_count=len(texts))


@pytest.mark.asyncio
async def test_multilingual_semantic_match_preserves_source_paragraphs() -> None:
    relevant = "La règle de conflit désigne la loi suisse comme loi applicable au contrat."
    text = "Historique de la procédure.\n\n" + ("Faits sans rapport. " * 200) + f"\n\n{relevant}\n\nDispositif."
    doc = DocumentContext(draft_id=1, text=text, semantic_embedder=_embed)
    result = await retrieve_choice_of_law_candidates(doc, ["loi applicable"], max_candidates=6)
    assert result.semantic_available is True
    assert any(relevant in candidate.text for candidate in result.candidates)
    assert any("semantic" in candidate.retrieval_methods for candidate in result.candidates)


@pytest.mark.asyncio
async def test_embedding_failure_activates_lexical_fallback() -> None:
    async def fail(_texts: list[str]) -> EmbeddingBatch:
        raise RuntimeError("embedding service unavailable")

    relevant = "The governing law is the law of Switzerland."
    doc = DocumentContext(draft_id=1, text=f"Background.\n\n{relevant}\n\nCosts.", semantic_embedder=fail)
    result = await retrieve_choice_of_law_candidates(doc, ["governing law"])
    assert result.semantic_available is False
    assert result.semantic_unavailable_reason == "RuntimeError"
    assert result.candidates
    assert any(relevant in candidate.text for candidate in result.candidates)
    assert result.lexical_hit_count > 0


@pytest.mark.asyncio
async def test_overlapping_hits_are_merged_and_deduplicated() -> None:
    text = "\n\n".join(
        [
            "Background.",
            "The parties made a choice of law.",
            "The governing law is Swiss law.",
            "The court applies that law.",
            "Costs.",
        ]
    )
    doc = DocumentContext(draft_id=1, text=text, semantic_embedder=_embed)
    result = await retrieve_choice_of_law_candidates(doc, ["choice of law", "governing law"])
    ranges = [(candidate.start_paragraph, candidate.end_paragraph) for candidate in result.candidates]
    assert len(ranges) == len(set(ranges))
    for left, right in zip(ranges, ranges[1:], strict=False):
        assert left[1] < right[0]
