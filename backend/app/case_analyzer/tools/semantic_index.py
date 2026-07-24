"""Request-scoped semantic index for court-decision paragraphs."""

from __future__ import annotations

import math
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

import logfire

from ..config import get_openai_client

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 64
CHUNK_MAX_CHARS = 2400
CHUNK_OVERLAP_PARAGRAPHS = 1


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: list[list[float]]
    token_count: int = 0


type EmbedFunction = Callable[[list[str]], Awaitable[EmbeddingBatch]]


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    start_paragraph: int
    end_paragraph: int


@dataclass(frozen=True)
class SemanticHit:
    chunk: DocumentChunk
    score: float
    query: str


def chunk_paragraphs(
    paragraphs: Sequence[str],
    *,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap_paragraphs: int = CHUNK_OVERLAP_PARAGRAPHS,
) -> list[DocumentChunk]:
    """Create paragraph-preserving chunks with paragraph overlap."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    if overlap_paragraphs < 0:
        raise ValueError("overlap_paragraphs cannot be negative")

    chunks: list[DocumentChunk] = []
    start = 0
    while start < len(paragraphs):
        end = start
        char_count = 0
        while end < len(paragraphs):
            separator_chars = 2 if end > start else 0
            next_count = char_count + separator_chars + len(paragraphs[end])
            if end > start and next_count > max_chars:
                break
            char_count = next_count
            end += 1

        chunks.append(
            DocumentChunk(
                text="\n\n".join(paragraphs[start:end]),
                start_paragraph=start + 1,
                end_paragraph=end,
            )
        )
        if end == len(paragraphs):
            break
        start = max(start + 1, end - overlap_paragraphs)
    return chunks


async def create_openai_embeddings(texts: list[str]) -> EmbeddingBatch:
    """Embed a batch and restore input order using response indices."""
    if not texts:
        return EmbeddingBatch(vectors=[])
    response = await get_openai_client().embeddings.create(input=texts, model=EMBEDDING_MODEL)
    ordered = sorted(response.data, key=lambda item: item.index)
    if [item.index for item in ordered] != list(range(len(texts))):
        raise ValueError("Embedding response indices did not match the request inputs")
    return EmbeddingBatch(
        vectors=[item.embedding for item in ordered],
        token_count=response.usage.total_tokens,
    )


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions do not match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


class SemanticIndex:
    """Embeddings and ranking state owned by one document analysis."""

    def __init__(self, paragraphs: Sequence[str], embed: EmbedFunction | None = None) -> None:
        self.chunks = chunk_paragraphs(paragraphs)
        self._embed = embed or create_openai_embeddings
        self._vectors: list[list[float]] = []
        self.embedding_tokens = 0

    async def build(self) -> None:
        with logfire.span(
            "semantic_index.build",
            chunk_count=len(self.chunks),
            paragraph_count=self.chunks[-1].end_paragraph if self.chunks else 0,
        ):
            vectors: list[list[float]] = []
            for batch_start in range(0, len(self.chunks), EMBEDDING_BATCH_SIZE):
                batch = self.chunks[batch_start : batch_start + EMBEDDING_BATCH_SIZE]
                response = await self._embed([chunk.text for chunk in batch])
                if len(response.vectors) != len(batch):
                    raise ValueError("Embedding response count did not match chunk count")
                vectors.extend(response.vectors)
                self.embedding_tokens += response.token_count
            if vectors and any(len(vector) != len(vectors[0]) for vector in vectors):
                raise ValueError("Document embeddings have inconsistent dimensions")
            self._vectors = vectors
            logfire.info(
                "Semantic index built",
                chunk_count=len(self.chunks),
                embedding_tokens=self.embedding_tokens,
            )

    async def embed_queries(self, queries: list[str]) -> EmbeddingBatch:
        response = await self._embed(queries)
        self.embedding_tokens += response.token_count
        return response

    def rank(self, query: str, vector: Sequence[float], *, top_k: int) -> list[SemanticHit]:
        scored = [
            SemanticHit(chunk=chunk, score=cosine_similarity(vector, chunk_vector), query=query)
            for chunk, chunk_vector in zip(self.chunks, self._vectors, strict=True)
        ]
        return sorted(scored, key=lambda hit: (-hit.score, hit.chunk.start_paragraph))[:top_k]
