"""Tests for case analyzer semantic and evidence policies."""

from app.case_analyzer.tools.models import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
)
from app.case_analyzer.validation import (
    validate_abstract,
    validate_case_citation,
    validate_col_issue,
    validate_col_section,
    validate_courts_position,
    validate_dissenting_opinions,
    validate_obiter_dicta,
    validate_pil_provisions,
    validate_relevant_facts,
    validate_themes,
)

NO_TOOLS = frozenset[str]()
SEARCH_USED = frozenset({"search"})
HEADINGS_ONLY = frozenset({"list_headings"})


def test_col_section_requires_content_bearing_tool() -> None:
    output = ColSectionOutput(col_sections=["The parties chose Swiss law."], confidence="high", reasoning="Located it.")
    assert validate_col_section(output, NO_TOOLS) is not None
    assert validate_col_section(output, HEADINGS_ONLY) is not None
    assert validate_col_section(output, SEARCH_USED) is None


def test_negative_citation_requires_navigation_evidence() -> None:
    output = CaseCitationOutput(
        case_citation="NA",
        source_text=None,
        source_location=None,
        identifier_type=None,
        confidence="low",
        reasoning="No citation found.",
    )
    assert validate_case_citation(output, NO_TOOLS) is not None
    assert validate_case_citation(output, SEARCH_USED) is None


def test_positive_citation_uses_supplied_prompt_evidence() -> None:
    output = CaseCitationOutput(
        case_citation="BGE 150 III 123",
        source_text="BGE 150 III 123",
        source_location="document beginning",
        identifier_type="reporter citation",
        confidence="high",
        reasoning="Found in the header.",
    )
    assert validate_case_citation(output, NO_TOOLS) is None


def test_positive_citation_requires_complete_source_evidence() -> None:
    output = CaseCitationOutput(
        case_citation="BGE 150 III 123",
        source_text="Different identifier",
        source_location="document beginning",
        identifier_type="reporter citation",
        confidence="high",
        reasoning="Found in the header.",
    )
    assert validate_case_citation(output, NO_TOOLS) is not None


def test_negative_citation_rejects_positive_source_evidence() -> None:
    output = CaseCitationOutput(
        case_citation="NA",
        source_text="Some identifier",
        source_location="document beginning",
        identifier_type="docket number",
        confidence="low",
        reasoning="No citation found.",
    )
    assert validate_case_citation(output, SEARCH_USED) is not None


def test_negative_citation_normalizes_placeholder_source_evidence() -> None:
    output = CaseCitationOutput(
        case_citation="NA",
        source_text="N/A",
        source_location="none",
        identifier_type="unknown",
        confidence="low",
        reasoning="No citation found.",
    )
    assert output.source_text is None
    assert output.source_location is None
    assert output.identifier_type is None
    assert validate_case_citation(output, SEARCH_USED) is None


def test_negative_citation_rejects_high_confidence() -> None:
    output = CaseCitationOutput(
        case_citation="NA",
        source_text=None,
        source_location=None,
        identifier_type=None,
        confidence="high",
        reasoning="No citation found.",
    )
    assert validate_case_citation(output, SEARCH_USED) is not None


def test_negative_theme_and_provisions_require_navigation_evidence() -> None:
    themes = ThemeClassificationOutput(themes=["NA"], confidence="low", reasoning="No matching theme.")
    provisions = PILProvisionsOutput(pil_provisions=[], confidence="low", reasoning="No provisions found.")
    assert validate_themes(themes, NO_TOOLS) is not None
    assert validate_themes(themes, SEARCH_USED) is None
    assert validate_pil_provisions(provisions, NO_TOOLS) is not None
    assert validate_pil_provisions(provisions, SEARCH_USED) is None


def test_negative_common_law_outputs_require_navigation_evidence() -> None:
    obiter = ObiterDictaOutput(
        obiter_dicta="No obiter dicta on choice of law issues identified",
        confidence="medium",
        reasoning="No relevant observations.",
    )
    dissent = DissentingOpinionsOutput(
        dissenting_opinions="No dissenting opinions on choice of law were identified",
        confidence="medium",
        reasoning="No relevant dissent.",
    )
    assert validate_obiter_dicta(obiter, NO_TOOLS) is not None
    assert validate_obiter_dicta(obiter, SEARCH_USED) is None
    assert validate_dissenting_opinions(dissent, NO_TOOLS) is not None
    assert validate_dissenting_opinions(dissent, SEARCH_USED) is None


def test_semantic_text_validators_reject_placeholders() -> None:
    facts = RelevantFactsOutput(relevant_facts="NA", confidence="low", reasoning="None.")
    issue = ColIssueOutput(col_issue="NA", confidence="low", reasoning="None.")
    position = CourtsPositionOutput(courts_position="NA", confidence="low", reasoning="None.")
    abstract = AbstractOutput(abstract="NA", confidence="low", reasoning="None.")
    assert validate_relevant_facts(facts, NO_TOOLS) is not None
    assert validate_col_issue(issue, NO_TOOLS) is not None
    assert validate_courts_position(position, NO_TOOLS) is not None
    assert validate_abstract(abstract, NO_TOOLS) is not None
