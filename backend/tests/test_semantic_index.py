"""Tests for the request-scoped in-memory semantic index."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.semantic_index import (
    EmbeddingBatch,
    SemanticIndex,
    chunk_paragraphs,
    cosine_similarity,
    create_openai_embeddings,
)


def test_chunking_preserves_paragraph_numbers_and_overlap() -> None:
    chunks = chunk_paragraphs(["a" * 6, "b" * 6, "c" * 6], max_chars=14, overlap_paragraphs=1)
    assert [(chunk.start_paragraph, chunk.end_paragraph) for chunk in chunks] == [(1, 2), (2, 3)]
    assert chunks[0].text == f"{'a' * 6}\n\n{'b' * 6}"


def test_cosine_similarity_ranks_direction_not_magnitude() -> None:
    assert cosine_similarity([1.0, 0.0], [3.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 2.0]) == pytest.approx(0.0)
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


@pytest.mark.asyncio
async def test_openai_embedding_response_is_restored_to_input_order() -> None:
    response = SimpleNamespace(
        data=[
            SimpleNamespace(index=1, embedding=[0.0, 1.0]),
            SimpleNamespace(index=0, embedding=[1.0, 0.0]),
        ],
        usage=SimpleNamespace(total_tokens=7),
    )
    client = MagicMock()
    client.embeddings.create = AsyncMock(return_value=response)
    with patch("app.case_analyzer.tools.semantic_index.get_openai_client", return_value=client):
        result = await create_openai_embeddings(["first", "second"])
    assert result == EmbeddingBatch(vectors=[[1.0, 0.0], [0.0, 1.0]], token_count=7)


@pytest.mark.asyncio
async def test_document_embeddings_are_generated_in_batches() -> None:
    calls: list[list[str]] = []

    async def embed(texts: list[str]) -> EmbeddingBatch:
        calls.append(texts)
        return EmbeddingBatch(vectors=[[1.0, 0.0] for _text in texts])

    index = SemanticIndex(["a" * 2500, "b" * 2500, "c" * 2500], embed=embed)
    with patch("app.case_analyzer.tools.semantic_index.EMBEDDING_BATCH_SIZE", 2):
        await index.build()
    assert [len(batch) for batch in calls] == [2, 1]


@pytest.mark.asyncio
async def test_concurrent_access_builds_only_one_index() -> None:
    calls = 0

    async def embed(texts: list[str]) -> EmbeddingBatch:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return EmbeddingBatch(vectors=[[1.0, 0.0] for _text in texts])

    doc = DocumentContext(draft_id=1, text="first paragraph\n\nsecond paragraph", semantic_embedder=embed)
    first, second, third = await asyncio.gather(doc.get_semantic_index(), doc.get_semantic_index(), doc.get_semantic_index())
    assert first is second is third
    assert calls == 1


@pytest.mark.asyncio
async def test_query_embeddings_are_cached_per_document() -> None:
    calls: list[list[str]] = []

    async def embed(texts: list[str]) -> EmbeddingBatch:
        calls.append(texts)
        return EmbeddingBatch(vectors=[[1.0, 0.0] for _text in texts])

    doc = DocumentContext(draft_id=1, text="The governing law is Swiss law.", semantic_embedder=embed)
    await doc.semantic_search(["governing law"])
    await doc.semantic_search(["governing law"])
    assert calls == [["The governing law is Swiss law."], ["governing law"]]


@pytest.mark.asyncio
async def test_embedding_failure_sets_explicit_unavailable_state() -> None:
    async def fail(_texts: list[str]) -> EmbeddingBatch:
        raise RuntimeError("offline")

    doc = DocumentContext(draft_id=1, text="The governing law is Swiss law.", semantic_embedder=fail)
    assert await doc.semantic_search(["governing law"]) == {}
    assert doc.semantic_unavailable_reason == "RuntimeError"
    assert await doc.get_semantic_index() is None
