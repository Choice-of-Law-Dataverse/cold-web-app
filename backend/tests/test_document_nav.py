"""Tests for document navigation tools and DocumentContext."""

import json
from typing import Any

import pytest
from agents.tool_context import ToolContext
from agents.usage import Usage

from app.case_analyzer.tools.document_nav import (
    DocumentContext,
    _detect_headings,
    _truncate,
    get_paragraph_containing,
    list_headings,
    read_head,
    read_section,
    read_tail,
    read_window,
    search,
)

FIXTURE_TEXT = """# Introduction

This case concerns the choice of law applicable to a contractual dispute.
The plaintiff, Acme Corp, argues that Swiss law should apply under Art. 3 IPRG.

## Background Facts

The parties entered into a sales agreement in 2019.
Both parties are domiciled in different jurisdictions.
The contract contained no explicit choice of law clause.

## Legal Analysis

The court must determine which law governs the dispute.
Under the Rome I Regulation, party autonomy is the primary connecting factor.

CHOICE OF LAW SECTION

The applicable law shall be determined by the habitual residence of the
characteristic performer. The defendant's domicile is in France.
Therefore, French law applies to the substantive dispute.

## Conclusion

The court dismisses the plaintiff's claims under Swiss law.
The parties shall bear their own costs."""

MAX_CHARS = 4000


@pytest.fixture
def doc() -> DocumentContext:
    return DocumentContext(draft_id=42, text=FIXTURE_TEXT)


def _make_ctx(doc_ctx: DocumentContext) -> ToolContext[DocumentContext]:
    return ToolContext(
        context=doc_ctx,
        usage=Usage(),
        tool_name="test",
        tool_call_id="test-id",
        tool_arguments="{}",
    )


async def _invoke(tool: Any, ctx: ToolContext[DocumentContext], args: dict[str, Any]) -> str:
    return await tool.on_invoke_tool(ctx, json.dumps(args))


class TestDocumentContext:
    def test_paragraphs_split_on_blank_lines(self, doc: DocumentContext) -> None:
        assert len(doc.paragraphs) > 0
        assert all(p.strip() for p in doc.paragraphs)

    def test_headings_detected(self, doc: DocumentContext) -> None:
        heading_texts = [h for h, _ in doc.headings]
        assert any("Introduction" in h for h in heading_texts)
        assert any("Background" in h for h in heading_texts)
        assert any("Legal" in h for h in heading_texts)

    def test_all_caps_heading_detected(self, doc: DocumentContext) -> None:
        heading_texts = [h for h, _ in doc.headings]
        assert any("CHOICE OF LAW" in h for h in heading_texts)

    def test_draft_id_stored(self, doc: DocumentContext) -> None:
        assert doc.draft_id == 42

    def test_empty_paragraphs_filtered(self) -> None:
        text = "Para one\n\n\n\n\nPara two"
        ctx = DocumentContext(draft_id=1, text=text)
        assert len(ctx.paragraphs) == 2


class TestTruncate:
    def test_short_text_unchanged(self) -> None:
        text = "hello"
        assert _truncate(text) == text

    def test_long_text_truncated(self) -> None:
        text = "x" * (MAX_CHARS + 100)
        result = _truncate(text)
        assert result.startswith("x" * MAX_CHARS)
        assert "[truncated: 100 chars remaining]" in result

    def test_exactly_max_chars_unchanged(self) -> None:
        text = "y" * MAX_CHARS
        assert _truncate(text) == text


class TestDetectHeadings:
    def test_markdown_heading_detected(self) -> None:
        paragraphs = ["# My Heading", "Some body text.", "## Sub-heading"]
        headings = _detect_headings(paragraphs)
        assert len(headings) == 2
        assert headings[0] == ("# My Heading", 0)
        assert headings[1] == ("## Sub-heading", 2)

    def test_all_caps_heading_detected(self) -> None:
        paragraphs = ["CHOICE OF LAW", "The applicable law is..."]
        headings = _detect_headings(paragraphs)
        assert any("CHOICE OF LAW" in h for h, _ in headings)

    def test_plain_body_not_a_heading(self) -> None:
        paragraphs = ["The court held that Article 3 applies."]
        assert _detect_headings(paragraphs) == []


class TestSearchTool:
    @pytest.mark.asyncio
    async def test_exact_match_found(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "party autonomy"})
        assert "party autonomy" in result.lower()

    @pytest.mark.asyncio
    async def test_case_insensitive(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "PLAINTIFF"})
        assert "plaintiff" in result.lower()

    @pytest.mark.asyncio
    async def test_no_match_returns_sentinel(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "quantum mechanics"})
        assert result == "[no matches]"

    @pytest.mark.asyncio
    async def test_fuzzy_fallback(self) -> None:
        text = "The applicable jurisdiction is Switzerland.\n\nOther paragraph here."
        result = await _invoke(
            search, _make_ctx(DocumentContext(draft_id=1, text=text)), {"query": "applicable jurisdiction Switzerland"}
        )
        assert "Switzerland" in result

    @pytest.mark.asyncio
    async def test_max_results_respected(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "the", "max_results": 2})
        assert result.count("---") <= 1


class TestGetParagraphContaining:
    @pytest.mark.asyncio
    async def test_returns_full_paragraph(self, doc: DocumentContext) -> None:
        result = await _invoke(get_paragraph_containing, _make_ctx(doc), {"text_snippet": "Acme Corp"})
        assert "Acme Corp" in result
        assert len(result) > len("Acme Corp")

    @pytest.mark.asyncio
    async def test_not_found_returns_sentinel(self, doc: DocumentContext) -> None:
        result = await _invoke(get_paragraph_containing, _make_ctx(doc), {"text_snippet": "nonexistent phrase xyz"})
        assert result == "[not found]"


class TestListHeadings:
    @pytest.mark.asyncio
    async def test_lists_headings_in_order(self, doc: DocumentContext) -> None:
        result = await _invoke(list_headings, _make_ctx(doc), {})
        assert "1." in result
        assert "Introduction" in result

    @pytest.mark.asyncio
    async def test_no_headings_sentinel(self) -> None:
        result = await _invoke(list_headings, _make_ctx(DocumentContext(draft_id=1, text="just plain text here")), {})
        assert result == "[no headings detected]"


class TestReadSection:
    @pytest.mark.asyncio
    async def test_reads_named_section(self, doc: DocumentContext) -> None:
        result = await _invoke(read_section, _make_ctx(doc), {"heading": "Background Facts"})
        assert "sales agreement" in result

    @pytest.mark.asyncio
    async def test_missing_heading_returns_sentinel(self, doc: DocumentContext) -> None:
        result = await _invoke(read_section, _make_ctx(doc), {"heading": "Nonexistent Section"})
        assert result == "[heading not found]"

    @pytest.mark.asyncio
    async def test_section_ends_at_next_heading(self, doc: DocumentContext) -> None:
        result = await _invoke(read_section, _make_ctx(doc), {"heading": "Background Facts"})
        assert "party autonomy" not in result


class TestReadWindow:
    @pytest.mark.asyncio
    async def test_returns_surrounding_text(self, doc: DocumentContext) -> None:
        result = await _invoke(read_window, _make_ctx(doc), {"anchor": "Rome I Regulation"})
        assert "Rome I Regulation" in result

    @pytest.mark.asyncio
    async def test_missing_anchor_returns_sentinel(self, doc: DocumentContext) -> None:
        result = await _invoke(read_window, _make_ctx(doc), {"anchor": "xyz nonexistent"})
        assert result == "[anchor not found]"

    @pytest.mark.asyncio
    async def test_window_boundaries_clamped(self) -> None:
        text = "short text"
        result = await _invoke(
            read_window,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"anchor": "short", "chars_before": 5000, "chars_after": 5000},
        )
        assert result == text


class TestReadHeadTail:
    @pytest.mark.asyncio
    async def test_read_head_returns_beginning(self, doc: DocumentContext) -> None:
        result = await _invoke(read_head, _make_ctx(doc), {"n_chars": 100})
        assert result == doc.text[:100]

    @pytest.mark.asyncio
    async def test_read_tail_returns_end(self, doc: DocumentContext) -> None:
        result = await _invoke(read_tail, _make_ctx(doc), {"n_chars": 50})
        assert result == doc.text[-50:]
