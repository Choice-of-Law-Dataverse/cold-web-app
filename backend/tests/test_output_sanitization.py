from app.case_analyzer.tools.models import (
    ColIssueOutput,
    ColSectionOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
    _strip_repetitive_suffix,
)


class TestStripRepetitiveSuffix:
    def test_removes_pmid_loop(self):
        text = "Valid content here.} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A."
        assert _strip_repetitive_suffix(text) == "Valid content here."

    def test_removes_generic_repetition(self):
        text = "Good text. abc123 abc123 abc123 abc123 abc123"
        result = _strip_repetitive_suffix(text)
        assert "abc123" not in result or result.count("abc123") < 3

    def test_preserves_clean_text(self):
        text = "This is a perfectly normal legal analysis with no repetition."
        assert _strip_repetitive_suffix(text) == text

    def test_preserves_short_repetitions(self):
        text = "The court said: yes, yes, yes."
        assert _strip_repetitive_suffix(text) == text

    def test_empty_string(self):
        assert _strip_repetitive_suffix("") == ""


class TestModelSanitization:
    def test_col_issue_sanitized(self):
        output = ColIssueOutput(
            confidence="high",
            reasoning="Good reasoning.",
            col_issue="What law applies?} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A.",
        )
        assert "PMID" not in output.col_issue
        assert output.col_issue == "What law applies?"

    def test_col_section_verbatim_source_text_is_not_sanitized(self):
        source_text = "Section 1 text.} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A."
        output = ColSectionOutput(
            confidence="high",
            reasoning="ok",
            col_sections=[source_text, "Section 2 clean."],
        )
        assert output.col_sections[0] == source_text
        assert output.col_sections[1] == "Section 2 clean."

    def test_reasoning_also_sanitized(self):
        output = RelevantFactsOutput(
            confidence="medium",
            reasoning="Analysis done.} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A.",
            relevant_facts="Clean facts here.",
        )
        assert "PMID" not in output.reasoning

    def test_clean_output_unchanged(self):
        output = ColIssueOutput(
            confidence="high",
            reasoning="Solid reasoning based on Art. 3 IPRG.",
            col_issue="Can parties choose a law unconnected to their contract?",
        )
        assert output.col_issue == "Can parties choose a law unconnected to their contract?"
        assert output.reasoning == "Solid reasoning based on Art. 3 IPRG."


class TestThemeDedup:
    def test_duplicate_themes_collapsed(self):
        output = ThemeClassificationOutput(
            confidence="medium",
            reasoning="Multiple themes detected.",
            themes=["Rules of Law", "Absence of choice", "Rules of Law", "Rules of Law"],
        )
        assert output.themes == ["Rules of Law", "Absence of choice"]

    def test_unique_themes_unchanged(self):
        output = ThemeClassificationOutput(
            confidence="high",
            reasoning="Two distinct themes.",
            themes=["Party autonomy", "Public policy"],
        )
        assert output.themes == ["Party autonomy", "Public policy"]

    def test_first_occurrence_position_preserved(self):
        output = ThemeClassificationOutput(
            confidence="medium",
            reasoning="Order check.",
            themes=["Tacit choice", "Party autonomy", "Tacit choice"],
        )
        assert output.themes == ["Tacit choice", "Party autonomy"]
