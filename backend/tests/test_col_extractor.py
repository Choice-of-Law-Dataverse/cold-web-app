"""Tests for audited Choice of Law output assembly."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.case_analyzer.config import get_model
from app.case_analyzer.jev import NoulAnswer, SystemOneResponse
from app.case_analyzer.runner import OutputValidationError
from app.case_analyzer.tools import col_extractor
from app.case_analyzer.tools.col_extractor import _assemble_output, _retrieval_evidence, jev_candidates
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.hybrid_retrieval import MAX_MERGED_PARAGRAPHS, CandidatePassage, RetrievalResult
from app.case_analyzer.tools.models import ColCandidateAuditOutput, ColCandidateDecision, StepResult


def test_output_is_reconstructed_verbatim_with_paragraph_provenance() -> None:
    paragraphs = ["Background.", "The court reasons that Swiss law governs.", "Swiss law therefore applies."]
    doc = DocumentContext(draft_id=1, text="\n\n".join(paragraphs))
    candidate = CandidatePassage(
        candidate_id="C001",
        start_paragraph=1,
        end_paragraph=3,
        text=doc.text,
        concepts=("applicable_law",),
        retrieval_methods=("exact", "semantic"),
        reciprocal_rank_score=0.2,
        semantic_score=0.95,
    )
    audit = ColCandidateAuditOutput(
        decisions=[
            ColCandidateDecision(
                candidate_id="C001",
                disposition="include",
                reason="The court states its reasoning and conclusion.",
                role="court_holding",
                selected_paragraphs=[2, 3],
            )
        ],
        confidence="high",
        reasoning="The candidate contains the direct holding.",
    )

    output, provenance = _assemble_output(audit, [candidate], doc)

    assert output.col_sections == [f"{paragraphs[1]}\n\n{paragraphs[2]}"]
    assert provenance == [
        {
            "section_index": 0,
            "paragraphs": [2, 3],
            "role": "court_holding",
            "candidate_ids": ["C001"],
            "retrieval_methods": ["exact", "semantic"],
        }
    ]


def test_retrieval_evidence_contains_no_vectors_or_judgment_text() -> None:
    retrieval = RetrievalResult(
        candidates=[],
        query_count=9,
        semantic_available=False,
        semantic_unavailable_reason="APIConnectionError",
        semantic_embedding_tokens=0,
        semantic_chunk_count=4,
        lexical_hit_count=2,
        semantic_hit_count=0,
        overlap_count=0,
    )
    evidence = _retrieval_evidence(retrieval)
    assert evidence["lexical_fallback"] is True
    assert "vectors" not in evidence
    assert "text" not in evidence


def test_jev_candidates_group_relevant_runs_and_keep_unanswered_paragraphs() -> None:
    paragraphs = [f"Paragraph {n}." for n in range(1, 8)]
    doc = DocumentContext(draft_id=1, text="\n\n".join(paragraphs))
    candidates = jev_candidates(doc, [0.1, 0.9, 0.6, 0.05, None, 0.2, 0.4], threshold=0.3)
    assert [(c.start_paragraph, c.end_paragraph) for c in candidates] == [(2, 3), (5, 5), (7, 7)]
    assert [c.candidate_id for c in candidates] == ["C001", "C002", "C003"]
    assert candidates[0].text == "Paragraph 2.\n\nParagraph 3."
    assert candidates[0].retrieval_methods == ("jev",)


def test_jev_candidates_split_long_runs() -> None:
    doc = DocumentContext(draft_id=1, text="\n\n".join(f"P{n}." for n in range(1, 26)))
    candidates = jev_candidates(doc, [0.9] * 25)
    assert all(len(c.paragraph_numbers) <= MAX_MERGED_PARAGRAPHS for c in candidates)
    assert sorted(n for c in candidates for n in c.paragraph_numbers) == list(range(1, 26))


def test_jev_candidates_empty_when_nothing_is_relevant() -> None:
    doc = DocumentContext(draft_id=1, text="One.\n\nTwo.")
    assert jev_candidates(doc, [0.1, 0.2]) == []


def test_unanswered_paragraphs_rank_below_relevant_ones() -> None:
    doc = DocumentContext(draft_id=1, text="\n\n".join(f"{n} " + "x" * 2300 for n in range(20)))
    candidates = jev_candidates(doc, [None] * 10 + [0.9] * 10)
    assert [c.start_paragraph for c in candidates] == [11]


@pytest.mark.asyncio
async def test_paragraphs_unanswered_by_the_timeout_are_none(monkeypatch: pytest.MonkeyPatch) -> None:
    async def slow_for_second(step: str, state: str, questions: dict) -> SystemOneResponse:
        if state == "slow":
            await asyncio.sleep(5)
        return SystemOneResponse(model="jev-1", answers={"relevant": NoulAnswer(type="noul", noul=0.9)})

    monkeypatch.setattr(col_extractor, "ask_jev", slow_for_second)
    assert await col_extractor.jev_paragraph_probabilities(["fast", "slow"], timeout=0.2) == [0.9, None]


@pytest.mark.asyncio
async def test_audit_falls_back_to_the_stronger_model(monkeypatch: pytest.MonkeyPatch) -> None:
    doc = DocumentContext(draft_id=1, text="Background.\n\nThe court holds that Swiss law governs the contract.")
    monkeypatch.setattr(col_extractor, "jev_paragraph_probabilities", AsyncMock(return_value=[0.1, 0.9]))
    models: list[str] = []
    decision = ColCandidateDecision(
        candidate_id="C001", disposition="include", reason="Holding.", role="court_holding", selected_paragraphs=[2]
    )

    async def fake_run_agent(agent: Any, **_kwargs: Any) -> StepResult[ColCandidateAuditOutput]:
        models.append(agent.model.model)
        if len(models) == 1:
            raise OutputValidationError("No candidate was included.")
        return StepResult(ColCandidateAuditOutput(decisions=[decision], confidence="high", reasoning="ok"))

    monkeypatch.setattr(col_extractor, "run_agent", fake_run_agent)
    monkeypatch.setattr(col_extractor, "get_openai_client", MagicMock())
    step = await col_extractor.extract_col_section(doc)

    assert models == [get_model("col_section"), get_model("col_section_fallback")]
    assert step.evidence["audit_model"] == get_model("col_section_fallback")
    assert step.output.col_sections == ["The court holds that Swiss law governs the contract."]


@pytest.mark.asyncio
async def test_hybrid_retrieval_candidates_are_audited_by_the_stronger_model(monkeypatch: pytest.MonkeyPatch) -> None:
    doc = DocumentContext(draft_id=1, text="Background.\n\nThe court holds that Swiss law governs the contract.")
    monkeypatch.setattr(col_extractor, "jev_paragraph_probabilities", AsyncMock(return_value=[0.05, 0.1]))
    monkeypatch.setattr(col_extractor, "_generate_case_specific_queries", AsyncMock(return_value=[]))
    candidate = CandidatePassage(
        candidate_id="C001",
        start_paragraph=2,
        end_paragraph=2,
        text=doc.paragraphs[1],
        concepts=("applicable_law",),
        retrieval_methods=("exact",),
        reciprocal_rank_score=0.2,
    )
    retrieval = RetrievalResult(
        candidates=[candidate],
        query_count=1,
        semantic_available=True,
        semantic_unavailable_reason=None,
        semantic_embedding_tokens=0,
        semantic_chunk_count=1,
        lexical_hit_count=1,
        semantic_hit_count=0,
        overlap_count=0,
    )
    monkeypatch.setattr(col_extractor, "retrieve_choice_of_law_candidates", AsyncMock(return_value=retrieval))
    models: list[str] = []
    decision = ColCandidateDecision(
        candidate_id="C001", disposition="include", reason="Holding.", role="court_holding", selected_paragraphs=[2]
    )

    async def fake_run_agent(agent: Any, **_kwargs: Any) -> StepResult[ColCandidateAuditOutput]:
        models.append(agent.model.model)
        return StepResult(ColCandidateAuditOutput(decisions=[decision], confidence="high", reasoning="ok"))

    monkeypatch.setattr(col_extractor, "run_agent", fake_run_agent)
    monkeypatch.setattr(col_extractor, "get_openai_client", MagicMock())
    step = await col_extractor.extract_col_section(doc)

    assert models == [get_model("col_section_fallback")]
    assert step.evidence["retrieval"]["method"] == "hybrid"
