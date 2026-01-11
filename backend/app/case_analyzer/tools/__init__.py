"""Case analyzer tools for extracting and analyzing court decision content."""

from .abstract_generator import extract_abstract
from .case_citation_extractor import extract_case_citation
from .col_extractor import extract_col_section
from .col_issue_extractor import extract_col_issue
from .courts_position_extractor import extract_courts_position
from .dissenting_opinions_extractor import extract_dissenting_opinions
from .jurisdiction_classifier import (
    create_jurisdiction_list,
    detect_precise_jurisdiction_with_confidence,
    load_jurisdictions,
)
from .jurisdiction_detector import (
    detect_legal_system_by_jurisdiction,
    get_jurisdiction_legal_system_mapping,
)
from .models import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
    ColSectionOutput,
    ConfidenceReasoningModel,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    JurisdictionOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
)
from .obiter_dicta_extractor import extract_obiter_dicta
from .pil_provisions_extractor import extract_pil_provisions
from .relevant_facts_extractor import extract_relevant_facts
from .theme_classifier import classify_themes

__all__ = [
    # Extraction functions
    "extract_abstract",
    "extract_case_citation",
    "extract_col_section",
    "extract_col_issue",
    "extract_courts_position",
    "extract_dissenting_opinions",
    "extract_obiter_dicta",
    "extract_pil_provisions",
    "extract_relevant_facts",
    # Classification functions
    "classify_themes",
    "detect_precise_jurisdiction_with_confidence",
    "detect_legal_system_by_jurisdiction",
    # Jurisdiction utilities
    "load_jurisdictions",
    "create_jurisdiction_list",
    "get_jurisdiction_legal_system_mapping",
    # Output models
    "AbstractOutput",
    "CaseCitationOutput",
    "ColIssueOutput",
    "ColSectionOutput",
    "ConfidenceReasoningModel",
    "CourtsPositionOutput",
    "DissentingOpinionsOutput",
    "JurisdictionOutput",
    "ObiterDictaOutput",
    "PILProvisionsOutput",
    "RelevantFactsOutput",
    "ThemeClassificationOutput",
]
