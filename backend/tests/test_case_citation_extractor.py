"""Tests for case-citation extraction prompt construction."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.case_analyzer.tools.case_citation_extractor import (
    _validate_citation_against_document,
    extract_case_citation,
)
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.models import CaseCitationOutput, StepResult


@pytest.mark.asyncio
async def test_extractor_receives_document_head_and_tail() -> None:
    head_citation = "BGE 150 III 123"
    tail_citation = "[2024] UKSC 42"
    middle_citation = "Pourvoi n° 24-18.329"
    omitted_marker = "THIS_UNRELATED_MIDDLE_MUST_BE_OMITTED"
    text = (
        f"{head_citation}\n"
        + ("H" * 5000)
        + omitted_marker
        + ("M" * 1000)
        + f"\nCour de cassation, première chambre civile, 11 février 2026, {middle_citation}\n"
        + ("T" * 5000)
        + f"\n{tail_citation}"
    )
    doc_ctx = DocumentContext(draft_id=1, text=text)
    expected = StepResult(
        output=CaseCitationOutput(
            case_citation=head_citation,
            source_text=head_citation,
            source_location="document beginning",
            identifier_type="reporter citation",
            confidence="high",
            reasoning="Found in the header.",
        ),
        response_id="response-1",
    )
    run_agent = AsyncMock(return_value=expected)

    with (
        patch("app.case_analyzer.tools.case_citation_extractor.Agent", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.OpenAIResponsesModel", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.get_openai_client", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.run_agent", run_agent),
    ):
        result = await extract_case_citation(doc_ctx, "Civil law", "Switzerland")

    run_call = run_agent.await_args
    assert run_call is not None
    prompt = run_call.kwargs["input"]
    prompt_text = prompt[0]["content"]
    assert head_citation in prompt_text
    assert tail_citation in prompt_text
    assert middle_citation not in prompt_text
    assert omitted_marker not in prompt_text
    assert "validate" not in run_call.kwargs
    assert _validate_citation_against_document(doc_ctx, expected.output, frozenset()) is None
    assert result == expected


@pytest.mark.asyncio
async def test_missing_citation_uses_navigation_model_fallback() -> None:
    doc_ctx = DocumentContext(
        draft_id=2,
        text="The extracted PDF text does not contain its own header.",
    )
    initial = StepResult(
        output=CaseCitationOutput(
            case_citation="NA",
            source_text=None,
            source_location=None,
            identifier_type=None,
            confidence="low",
            reasoning="Not found.",
        ),
        response_id="response-1",
    )
    expected = StepResult(output=initial.output, response_id="response-2", tool_names=("search",))
    run_agent = AsyncMock(side_effect=[initial, expected])

    with (
        patch("app.case_analyzer.tools.case_citation_extractor.Agent", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.OpenAIResponsesModel", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.get_openai_client", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.run_agent", run_agent),
    ):
        result = await extract_case_citation(doc_ctx, "Civil-law jurisdiction", "Switzerland")

    assert result == expected
    assert run_agent.await_count == 2
    first_call, second_call = run_agent.await_args_list
    assert "validate" not in first_call.kwargs
    assert "validate" in second_call.kwargs
    assert "navigation fallback" not in first_call.kwargs["input"][0]["content"]
    assert "Use the navigation tools" in second_call.kwargs["input"][0]["content"]


@pytest.mark.asyncio
async def test_filename_and_excerpts_are_supplied_to_one_model_pass() -> None:
    file_name = "4A_305_2025 13.03.2026.pdf"
    decision_text = "4A_305/2025 13.03.2026\nDecision text with unrelated choice-of-law analysis."
    doc_ctx = DocumentContext(draft_id=3, text=decision_text, file_name=file_name)
    expected = StepResult(
        output=CaseCitationOutput(
            case_citation="4A_305/2025",
            source_text="4A_305/2025",
            source_location="document beginning",
            identifier_type="docket number",
            confidence="high",
            reasoning="The filename and document header identify the decision as 4A_305/2025.",
        ),
        response_id="response-3",
    )
    run_agent = AsyncMock(return_value=expected)

    with (
        patch("app.case_analyzer.tools.case_citation_extractor.Agent", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.OpenAIResponsesModel", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.get_openai_client", MagicMock()),
        patch("app.case_analyzer.tools.case_citation_extractor.run_agent", run_agent),
    ):
        result = await extract_case_citation(doc_ctx, "Civil-law jurisdiction", "Switzerland")

    run_call = run_agent.await_args
    assert run_call is not None
    prompt = run_call.kwargs["input"]
    prompt_text = prompt[0]["content"]
    assert file_name in prompt_text
    assert "Identifier-like filename segments: 4A_305_2025" in prompt_text
    assert decision_text in prompt_text
    assert "validate" not in run_call.kwargs
    assert result.tool_names == ()
    assert result == expected


def test_validator_rejects_source_text_not_in_document() -> None:
    doc_ctx = DocumentContext(draft_id=3, text="Decision header without a citation.")
    output = CaseCitationOutput(
        case_citation="Invented 123",
        source_text="Invented 123",
        source_location="document beginning",
        identifier_type="docket number",
        confidence="high",
        reasoning="Claimed header match.",
    )

    assert _validate_citation_against_document(doc_ctx, output, frozenset()) is not None


def test_validator_requires_navigation_for_source_outside_supplied_excerpts() -> None:
    citation = "Tribunal reference 2026-XYZ"
    text = ("H" * 5000) + citation + ("T" * 5000)
    doc_ctx = DocumentContext(draft_id=4, text=text)
    output = CaseCitationOutput(
        case_citation=citation,
        source_text=citation,
        source_location="paragraph 1",
        identifier_type="docket number",
        confidence="high",
        reasoning="Found in the decision body.",
    )

    assert _validate_citation_against_document(doc_ctx, output, frozenset()) is not None
    assert _validate_citation_against_document(doc_ctx, output, frozenset({"search"})) is None


def test_validator_accepts_generic_filename_evidence_with_bounded_confidence() -> None:
    file_name = "4A_305_2025 13.03.2026.pdf"
    doc_ctx = DocumentContext(draft_id=5, text="Decision text without a printed identifier.", file_name=file_name)
    output = CaseCitationOutput(
        case_citation="4A_305/2025",
        source_text=file_name,
        source_location="original filename",
        identifier_type="docket number",
        confidence="medium",
        reasoning="The identifier is present only in the original filename.",
    )

    assert _validate_citation_against_document(doc_ctx, output, frozenset()) is None


def test_validator_rejects_high_confidence_for_filename_only_evidence() -> None:
    file_name = "decision-2026-XYZ.pdf"
    doc_ctx = DocumentContext(draft_id=6, text="Decision text without a printed identifier.", file_name=file_name)
    output = CaseCitationOutput(
        case_citation="2026-XYZ",
        source_text=file_name,
        source_location="original filename",
        identifier_type="docket number",
        confidence="high",
        reasoning="The identifier is present only in the original filename.",
    )

    assert _validate_citation_against_document(doc_ctx, output, frozenset()) is not None


def test_validator_rejects_na_when_filename_contains_strong_identifier_candidate() -> None:
    doc_ctx = DocumentContext(
        draft_id=7,
        text="Decision text without a printed identifier.",
        file_name="4A_305_2025 13.03.2026.pdf",
    )
    output = CaseCitationOutput(
        case_citation="NA",
        source_text=None,
        source_location=None,
        identifier_type=None,
        confidence="low",
        reasoning="No identifier found.",
    )

    error = _validate_citation_against_document(doc_ctx, output, frozenset({"search"}))

    assert error is not None
    assert "4A_305_2025" in error


def test_validator_rejects_adjacent_date_in_filename_citation() -> None:
    file_name = "4A_305_2025 13.03.2026.pdf"
    source_text = "4A_305/2025 13.03.2026"
    doc_ctx = DocumentContext(draft_id=8, text=f"{source_text}\nDecision text.", file_name=file_name)
    output = CaseCitationOutput(
        case_citation=source_text,
        source_text=source_text,
        source_location="document beginning",
        identifier_type="docket number",
        confidence="high",
        reasoning="Found in the document header.",
    )

    error = _validate_citation_against_document(doc_ctx, output, frozenset())

    assert error is not None
    assert "adjacent decision date" in error


def test_validator_rejects_verbose_or_issue_focused_reasoning() -> None:
    citation = "BGE 150 III 123"
    doc_ctx = DocumentContext(draft_id=9, text=citation)
    output = CaseCitationOutput(
        case_citation=citation,
        source_text=citation,
        source_location="document beginning",
        identifier_type="reporter citation",
        confidence="high",
        reasoning=" ".join(f"irrelevant-detail-{index}" for index in range(30)),
    )

    assert _validate_citation_against_document(doc_ctx, output, frozenset()) is not None
