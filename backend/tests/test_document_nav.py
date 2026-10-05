"""Tests for document navigation tools and DocumentContext."""

import json
import re
from typing import Any

import pytest
from agents.tool_context import ToolContext
from agents.usage import Usage

from app.case_analyzer.tools.document_nav import (
    MAX_PARAGRAPH_CHARS,
    NAV_TOOLS,
    DocumentContext,
    _detect_headings,
    _truncate,
    clean_document_text,
    get_paragraph_containing,
    list_headings,
    merge_fragments,
    read_head,
    read_paragraphs,
    read_section,
    read_tail,
    read_window,
    search,
    split_oversized_paragraph,
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
        text = "Para one " + "x" * 200 + "\n\n\n\n\nPara two " + "y" * 200
        ctx = DocumentContext(draft_id=1, text=text)
        assert len(ctx.paragraphs) == 2

    def test_normalized_paragraphs_are_precomputed(self, doc: DocumentContext) -> None:
        assert len(doc.normalized_paragraphs) == len(doc.paragraphs)


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

    def test_non_ascii_all_caps_heading_detected(self) -> None:
        paragraphs = ["RÈGLES DE CONFLIT", "La loi applicable est..."]
        headings = _detect_headings(paragraphs)
        assert headings == [("RÈGLES DE CONFLIT", 0)]

    def test_non_latin_all_caps_heading_detected(self) -> None:
        paragraphs = ["ПРИМЕНИМОЕ ПРАВО", "Суд установил применимое право."]
        headings = _detect_headings(paragraphs)
        assert headings == [("ПРИМЕНИМОЕ ПРАВО", 0)]

    def test_plain_body_not_a_heading(self) -> None:
        paragraphs = ["The court held that Article 3 applies."]
        assert _detect_headings(paragraphs) == []


class TestSearchTool:
    @pytest.mark.asyncio
    async def test_exact_match_found(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "party autonomy"})
        assert "party autonomy" in result.lower()
        assert "[paragraph " in result

    @pytest.mark.asyncio
    async def test_case_insensitive(self, doc: DocumentContext) -> None:
        result = await _invoke(search, _make_ctx(doc), {"query": "PLAINTIFF"})
        assert "plaintiff" in result.lower()

    @pytest.mark.asyncio
    async def test_multilingual_unicode_casefold(self) -> None:
        text = "Das maßgebliche Recht bestimmt sich nach dem engsten Zusammenhang."
        result = await _invoke(
            search,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"query": "MASSGEBLICHE RECHT"},
        )
        assert text in result

    @pytest.mark.asyncio
    async def test_accent_insensitive_search_preserves_source_text(self) -> None:
        text = "La loi étrangère régit les obligations contractuelles."
        result = await _invoke(
            search,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"query": "loi etrangere"},
        )
        assert text in result

    @pytest.mark.asyncio
    async def test_pdf_line_break_hyphenation_is_ignored(self) -> None:
        text = "Das anzuwen-\ndende Recht ist nach dem IPRG zu bestimmen."
        result = await _invoke(
            search,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"query": "anzuwendende Recht"},
        )
        assert text in result

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
    async def test_matches_normalized_multilingual_snippet(self) -> None:
        text = "La règle de conflit désigne la loi applicable."
        result = await _invoke(
            get_paragraph_containing,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"text_snippet": "regle de conflit"},
        )
        assert text in result


class TestReadParagraphs:
    @pytest.mark.asyncio
    async def test_reads_search_hit_and_following_paragraph(self, doc: DocumentContext) -> None:
        search_result = await _invoke(search, _make_ctx(doc), {"query": "Background Facts"})
        paragraph_number = int(re.search(r"\[paragraph (\d+)\]", search_result).group(1))  # type: ignore[union-attr]

        result = await _invoke(
            read_paragraphs,
            _make_ctx(doc),
            {"start_paragraph": paragraph_number, "count": 2},
        )

        assert "Background Facts" in result
        assert "sales agreement" in result

    @pytest.mark.asyncio
    async def test_out_of_range_returns_sentinel(self, doc: DocumentContext) -> None:
        result = await _invoke(read_paragraphs, _make_ctx(doc), {"start_paragraph": 999})
        assert result == "[paragraph out of range]"

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

    @pytest.mark.asyncio
    async def test_case_insensitive_anchor(self, doc: DocumentContext) -> None:
        result = await _invoke(read_window, _make_ctx(doc), {"anchor": "rome i regulation"})
        assert "Rome I Regulation" in result

    @pytest.mark.asyncio
    async def test_window_alignment_with_expanding_lowercase(self) -> None:
        text = "İİİİİ karar metni uygulanacak hukuk hakkında"
        result = await _invoke(
            read_window,
            _make_ctx(DocumentContext(draft_id=1, text=text)),
            {"anchor": "uygulanacak hukuk", "chars_before": 0, "chars_after": 0},
        )
        assert result == "uygulanacak hukuk"


class TestReadHeadTail:
    @pytest.mark.asyncio
    async def test_read_head_returns_beginning(self, doc: DocumentContext) -> None:
        result = await _invoke(read_head, _make_ctx(doc), {"n_chars": 100})
        assert result == doc.text[:100]

    @pytest.mark.asyncio
    async def test_read_tail_returns_end(self, doc: DocumentContext) -> None:
        result = await _invoke(read_tail, _make_ctx(doc), {"n_chars": 50})
        assert result == doc.text[-50:]

    @pytest.mark.asyncio
    async def test_read_tail_zero_returns_end_not_start(self, doc: DocumentContext) -> None:
        result = await _invoke(read_tail, _make_ctx(doc), {"n_chars": 0})
        assert result == doc.text[-1:]

    @pytest.mark.asyncio
    async def test_read_head_zero_returns_first_char(self, doc: DocumentContext) -> None:
        result = await _invoke(read_head, _make_ctx(doc), {"n_chars": 0})
        assert result == doc.text[:1]


class TestNavToolsRoster:
    def test_preamble_matches_registered_tools(self) -> None:
        from app.case_analyzer.prompts.shared import NAV_TOOLS_PREAMBLE

        preamble_names = set(re.findall(r"- (\w+)\(", NAV_TOOLS_PREAMBLE))
        tool_names = {tool.name for tool in NAV_TOOLS}
        assert preamble_names == tool_names

    def test_all_extractor_agents_use_full_roster(self) -> None:
        import inspect
        from pathlib import Path

        import app.case_analyzer.tools as tools_pkg

        tools_dir = Path(inspect.getfile(tools_pkg)).parent
        extractor_files = list(tools_dir.glob("*_extractor.py")) + [
            tools_dir / "theme_classifier.py",
            tools_dir / "abstract_generator.py",
        ]
        for path in extractor_files:
            source = path.read_text()
            assert "tools=NAV_TOOLS" in source, f"{path.name} does not use NAV_TOOLS"
            assert "tools=[" not in source, f"{path.name} still hardcodes a tool list"


class TestOversizedParagraphs:
    def test_long_paragraph_splits_at_line_breaks(self) -> None:
        lines = [f"Line {n} " + "x" * 90 for n in range(60)]
        ctx = DocumentContext(draft_id=1, text="\n".join(lines))
        assert len(ctx.paragraphs) > 1
        assert all(len(p) <= MAX_PARAGRAPH_CHARS for p in ctx.paragraphs)
        assert "\n".join(ctx.paragraphs) == "\n".join(lines)

    def test_single_line_splits_at_sentence_ends(self) -> None:
        text = " ".join(f"Sentence {n} states a rule." for n in range(200))
        parts = split_oversized_paragraph(text, max_chars=500)
        assert all(len(p) <= 500 for p in parts)
        assert all(p.endswith(".") for p in parts)
        assert " ".join(parts) == text

    def test_text_without_whitespace_is_cut_to_size(self) -> None:
        assert split_oversized_paragraph("x" * 1050, max_chars=500) == ["x" * 500, "x" * 500, "x" * 50]

    def test_pieces_keep_the_original_whitespace_between_sentences(self) -> None:
        text = "  ".join(f"Sentence {n} states\na rule." for n in range(200))
        parts = split_oversized_paragraph(text, max_chars=500)
        assert len(parts) > 1
        assert all(len(p) <= 500 and p in text for p in parts)
        assert any("rule.  Sentence" in p for p in parts)

    def test_every_paragraph_is_verbatim_document_text(self) -> None:
        wrapped = "  ".join(f"Sentence {n} of the reasons\nwraps onto a second line." for n in range(120))
        facts = "The parties  signed a sales contract\nin 2019 and later disputed the price. " * 4
        text = (
            f"Judgment of 3 May 2020\n\nBefore the court.\n\n{facts}\n\n{wrapped}\n\n"
            f"## Applicable law\n\n{wrapped}\n\nSigned.\n\nJudge X"
        )
        ctx = DocumentContext(draft_id=1, text=text)
        assert len(ctx.paragraphs) > 4
        assert all(len(p) <= MAX_PARAGRAPH_CHARS for p in ctx.paragraphs)
        assert all(p in ctx.text for p in ctx.paragraphs)
        assert ctx.paragraphs[0].startswith("Judgment of 3 May 2020\n\nBefore the court.\n\nThe parties  signed")
        assert ctx.paragraphs[-1].endswith("wraps onto a second line.\n\nSigned.\n\nJudge X")
        assert ("## Applicable law", next(i for i, p in enumerate(ctx.paragraphs) if p.startswith("##"))) in ctx.headings


class TestFragmentMerging:
    body = "The court finds that the parties chose Swiss law for their contract. " * 4

    def test_fragments_join_the_paragraph_after_them(self) -> None:
        assert merge_fragments(["Page 3", "1.", self.body]) == [f"Page 3\n\n1.\n\n{self.body}"]

    def test_heading_starts_its_merged_paragraph_and_is_still_detected(self) -> None:
        ctx = DocumentContext(draft_id=1, text=f"Judgment of 3 May\n\n## Applicable law\n\n{self.body}")
        assert ctx.paragraphs == ["Judgment of 3 May", f"## Applicable law\n\n{self.body.strip()}"]
        assert ctx.headings == [("## Applicable law", 1)]

    def test_trailing_fragments_join_the_paragraph_before_them(self) -> None:
        assert merge_fragments([self.body, "Signed.", "Judge X"]) == [f"{self.body}\n\nSigned.\n\nJudge X"]

    def test_merging_never_exceeds_the_paragraph_limit(self) -> None:
        long_body = "y" * (MAX_PARAGRAPH_CHARS - 10)
        assert merge_fragments(["z" * 150, long_body]) == ["z" * 150, long_body]


class TestCleanDocumentText:
    header = "ESTADO DO RIO GRANDE DO SUL PODER JUDICIÁRIO TRIBUNAL DE JUSTIÇA"

    def _pages(self, bodies: list[str]) -> str:
        return "\n\n".join(f"{body}\n\n{number}\n\n{self.header}" for number, body in enumerate(bodies, start=1))

    def test_running_header_keeps_its_first_occurrence(self) -> None:
        text = clean_document_text(self._pages([f"Paragraph {n} ends here." for n in range(6)]))
        assert text.count(self.header) == 1

    def test_sentence_split_by_a_page_break_is_rejoined(self) -> None:
        bodies = ["Filler sentence one.", "Filler two.", "Basta que uma das", "partes seja domiciliada.", "End.", "Done."]
        text = clean_document_text(self._pages(bodies))
        assert "Basta que uma das partes seja domiciliada." in text

    def test_bare_number_inside_a_sentence_goes_but_a_paragraph_number_stays(self) -> None:
        assert clean_document_text("The court held that the\n\n16\n\ncontract was valid.") == (
            "The court held that the contract was valid."
        )
        assert clean_document_text("Introduction.\n\n49.\n\nThe parties chose Swiss law.") == (
            "Introduction.\n\n49.\n\nThe parties chose Swiss law."
        )

    def test_page_markers_go(self) -> None:
        for marker in ("- 12 -", "Page 4", "Página 25 de 69", "36/58", "#### - 20 -"):
            assert clean_document_text(f"First.\n\n{marker}\n\nSecond.") == "First.\n\nSecond."

    def test_repeated_table_cells_footnotes_and_quoted_sentences_stay(self) -> None:
        cells = "\n\n".join(["Date", "$10 million", "12 April", "$10 million", "13 April", "$10 million"])
        footnotes = "\n\n".join(
            f"- {n} Mercantile Mutual Insurance v Neilson (2004) 28 WAR 206 at {200 + n}." for n in range(5)
        )
        quote = "The contract is governed by the law of the seller's habitual residence."
        filler = "\n\n".join(f"Paragraph {n} of the reasons." for n in range(20))
        text = clean_document_text(f"{cells}\n\n{filler}\n\n{footnotes}\n\n{quote}\n\n{filler}\n\n{quote}\n\n{quote}")
        assert text.count("$10 million") == 3
        assert text.count("Mercantile Mutual") == 5
        assert text.count(quote) == 3

    def test_line_break_tags_become_spaces(self) -> None:
        assert clean_document_text("applicable<br>law") == "applicable law"
        assert clean_document_text("BANK OF INDIA<br/>and | Swiss <BR /> law") == "BANK OF INDIA and | Swiss law"
        assert clean_document_text("the parties<br>, however") == "the parties, however"

    def test_inline_markup_is_removed_but_identifiers_keep_underscores(self) -> None:
        text = clean_document_text("**_1-_** _contrato internacional_ , em outro._<sup>6</sup> BGer 4A_543/2018")
        assert text == "1- contrato internacional, em outro.⁶ BGer 4A_543/2018"

    def test_short_picture_text_goes_and_long_picture_text_stays(self) -> None:
        scanned = "The court finds that the parties chose the law of Brazil for the contract. " * 3
        text = clean_document_text(
            "<!-- Start of picture text -->esUDic, .Ss %<!-- End of picture text -->\n\n"
            f"<!-- Start of picture text -->{scanned}<!-- End of picture text -->"
        )
        assert text == scanned.strip()


class TestPageBreaks:
    header = "ESTADO DO RIO GRANDE DO SUL PODER JUDICIÁRIO TRIBUNAL DE JUSTIÇA"
    filler = "\n\n".join(f"Paragraph {n} of the reasons." for n in range(12))

    def test_page_number_mid_sentence_joins_a_capitalised_continuation(self) -> None:
        text = clean_document_text("Its members include China, Japan and South-East\n\n20\n\nAsia, among others.")
        assert text == "Its members include China, Japan and South-East Asia, among others."

    def test_footnotes_between_the_halves_move_after_the_sentence(self) -> None:
        text = clean_document_text(
            "the set of rules gathered in\n\n> 15 BROWNLIE, Principles, p. 6.\n\n21\n\nprinciples and usages."
        )
        assert text == "the set of rules gathered in principles and usages.\n\n> 15 BROWNLIE, Principles, p. 6."

    def test_bare_number_next_to_a_running_header_goes(self) -> None:
        pages = "\n\n".join(f"Sentence {n} ends here.\n\n{n}\n\n{self.header}\n\nUGS" for n in range(1, 6))
        text = clean_document_text(f"{pages}\n\n{self.filler}")
        assert text.count(self.header) == 1
        assert text.count("UGS") == 1
        assert "\n\n3\n\n" not in text
