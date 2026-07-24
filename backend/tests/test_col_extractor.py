"""Tests for audited Choice of Law output assembly."""

from app.case_analyzer.tools.col_extractor import _assemble_output, _retrieval_evidence
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.hybrid_retrieval import CandidatePassage, RetrievalResult
from app.case_analyzer.tools.models import ColCandidateAuditOutput, ColCandidateDecision


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
