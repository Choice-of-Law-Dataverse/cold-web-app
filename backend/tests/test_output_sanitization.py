from app.case_analyzer.tools.models import (
    ColIssueOutput,
    ColSectionOutput,
    RelevantFactsOutput,
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

    def test_col_section_list_sanitized(self):
        output = ColSectionOutput(
            confidence="high",
            reasoning="ok",
            col_sections=[
                "Section 1 text.} PMID: N/A.} PMID: N/A.} PMID: N/A.} PMID: N/A.",
                "Section 2 clean.",
            ],
        )
        assert "PMID" not in output.col_sections[0]
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
