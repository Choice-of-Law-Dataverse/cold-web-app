"""Sanitized annotated retrieval-quality baseline."""

import json
from pathlib import Path
from typing import Any

import pytest

from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.hybrid_retrieval import retrieve_choice_of_law_candidates
from app.case_analyzer.tools.semantic_index import EmbeddingBatch

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "col_retrieval_multilingual.json"


def _vector(text: str) -> list[float]:
    normalized = text.casefold()
    relevant_terms = (
        "law",
        "choice",
        "party autonomy",
        "clause",
        "droit",
        "loi",
        "conflit",
        "autonomie",
        "recht",
        "rechtswahl",
        "parteiautonomie",
        "anzuwenden",
    )
    return [1.0, 0.0] if any(term in normalized for term in relevant_terms) else [0.0, 1.0]


async def _embed(texts: list[str]) -> EmbeddingBatch:
    return EmbeddingBatch(vectors=[_vector(text) for text in texts], token_count=len(texts))


def _renumber(annotated: list[str], paragraphs: list[str]) -> dict[int, int]:
    """Map each annotated paragraph number to the DocumentContext paragraph holding its text.

    The padding pushes every annotated paragraph past the split limit, so DocumentContext renumbers them.
    """
    return {
        number: next(index for index, paragraph in enumerate(paragraphs, start=1) if text in paragraph)
        for number, text in enumerate(annotated, start=1)
    }


@pytest.mark.asyncio
async def test_annotated_candidate_recall_and_direct_holding_coverage() -> None:
    fixtures: list[dict[str, Any]] = json.loads(_FIXTURE_PATH.read_text())
    relevant_total = 0
    relevant_retrieved = 0
    irrelevant_total = 0
    irrelevant_retrieved = 0

    for draft_id, fixture in enumerate(fixtures, start=1):
        paragraphs: list[str] = [paragraph + (" Procedural chronology." * 120) for paragraph in fixture["paragraphs"]]
        doc = DocumentContext(draft_id=draft_id, text="\n\n".join(paragraphs), semantic_embedder=_embed)
        renumbered = _renumber(fixture["paragraphs"], doc.paragraphs)
        relevant = {renumbered[number] for number in fixture["relevant_paragraphs"]}
        holdings = {renumbered[number] for number in fixture["direct_holding_paragraphs"]}
        retrieval = await retrieve_choice_of_law_candidates(doc)
        retrieved = {number for candidate in retrieval.candidates for number in candidate.paragraph_numbers}

        relevant_total += len(relevant)
        relevant_retrieved += len(relevant & retrieved)
        irrelevant = set(range(1, len(doc.paragraphs) + 1)) - relevant
        irrelevant_total += len(irrelevant)
        irrelevant_retrieved += len(irrelevant & retrieved)
        assert holdings <= retrieved, f"missed direct holding in {fixture['name']}"

    candidate_recall = relevant_retrieved / relevant_total
    irrelevant_inclusion_rate = irrelevant_retrieved / irrelevant_total
    assert candidate_recall >= 0.95
    assert irrelevant_inclusion_rate <= 0.90
