"""
Case analysis service using tools from cold-case-analysis repository.
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

import logfire

from app.case_analysis.models import (
    ColSectionOutput,
    JurisdictionOutput,
)
from app.case_analysis.tools.abstract_generator import extract_abstract
from app.case_analysis.tools.case_citation_extractor import extract_case_citation
from app.case_analysis.tools.col_extractor import extract_col_section
from app.case_analysis.tools.col_issue_extractor import extract_col_issue
from app.case_analysis.tools.courts_position_extractor import extract_courts_position
from app.case_analysis.tools.jurisdiction_classifier import detect_precise_jurisdiction_with_confidence
from app.case_analysis.tools.jurisdiction_detector import detect_legal_system_type
from app.case_analysis.tools.pil_provisions_extractor import extract_pil_provisions
from app.case_analysis.tools.relevant_facts_extractor import extract_relevant_facts
from app.case_analysis.tools.theme_classifier import theme_classification_node
from app.case_analysis.utils.pdf_handler import extract_text_from_pdf

logger = logging.getLogger(__name__)


def detect_jurisdiction(text: str) -> JurisdictionOutput:
    """
    Detect jurisdiction from court decision text using two-step process.

    Args:
        text: Full court decision text

    Returns:
        JurisdictionOutput with legal system type, precise jurisdiction, and confidence
    """
    with logfire.span("jurisdiction_detection"):
        if not text or len(text.strip()) < 50:
            return JurisdictionOutput(
                legal_system_type="No court decision",
                precise_jurisdiction="Unknown",
                jurisdiction_code="XX",
                confidence="low",
                reasoning="Text too short for analysis",
            )

        # Step 1: Detect legal system type (Civil-law, Common-law, etc.)
        legal_system_type = detect_legal_system_type("", text)

        # Step 2: Classify precise jurisdiction
        jurisdiction_result = detect_precise_jurisdiction_with_confidence(text)

        return jurisdiction_result


async def analyze_case_streaming(
    text: str, jurisdiction_data: dict[str, Any]
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Execute complete case analysis workflow with streaming updates.

    Yields intermediate results as they complete.

    Args:
        text: Full court decision text
        jurisdiction_data: Dictionary containing jurisdiction information

    Yields:
        Dictionary with step name, status, and data for each analysis step
    """
    legal_system = jurisdiction_data["legal_system_type"]
    jurisdiction = jurisdiction_data["precise_jurisdiction"]

    with logfire.span("case_analysis_workflow"):
        # Step 1: Extract COL sections
        yield {"step": "col_extraction", "status": "in_progress"}

        try:
            col_result: ColSectionOutput = extract_col_section(text, legal_system, jurisdiction)
            yield {
                "step": "col_extraction",
                "status": "completed",
                "data": {
                    "col_sections": col_result.col_sections,
                    "confidence": col_result.confidence,
                    "reasoning": col_result.reasoning,
                },
            }
            col_sections = col_result.col_sections
            col_section_text = str(col_result)
        except Exception as e:
            logger.error("COL extraction failed: %s", str(e))
            yield {"step": "col_extraction", "status": "error", "error": str(e)}
            return

        # Step 2: Theme classification
        yield {"step": "theme_classification", "status": "in_progress"}
        try:
            theme_result = theme_classification_node(text, col_section_text, legal_system, jurisdiction)
            yield {
                "step": "theme_classification",
                "status": "completed",
                "data": {
                    "themes": theme_result.themes,
                    "confidence": theme_result.confidence,
                    "reasoning": theme_result.reasoning,
                },
            }
        except Exception as e:
            logger.error("Theme classification failed: %s", str(e))
            yield {"step": "theme_classification", "status": "error", "error": str(e)}

        # Step 3: Case citation
        yield {"step": "case_citation", "status": "in_progress"}
        try:
            citation_result = extract_case_citation(text, legal_system, jurisdiction)
            yield {
                "step": "case_citation",
                "status": "completed",
                "data": {
                    "case_citation": citation_result.case_citation,
                    "confidence": citation_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Case citation extraction failed: %s", str(e))
            yield {"step": "case_citation", "status": "error", "error": str(e)}

        # Step 4: Abstract
        yield {"step": "abstract", "status": "in_progress"}
        try:
            abstract_result = extract_abstract(col_section_text, legal_system, jurisdiction)
            yield {
                "step": "abstract",
                "status": "completed",
                "data": {
                    "abstract": abstract_result.abstract,
                    "confidence": abstract_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Abstract generation failed: %s", str(e))
            yield {"step": "abstract", "status": "error", "error": str(e)}

        # Step 5: Relevant facts
        yield {"step": "relevant_facts", "status": "in_progress"}
        try:
            facts_result = extract_relevant_facts(col_section_text, legal_system, jurisdiction)
            yield {
                "step": "relevant_facts",
                "status": "completed",
                "data": {
                    "relevant_facts": facts_result.relevant_facts,
                    "confidence": facts_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Facts extraction failed: %s", str(e))
            yield {"step": "relevant_facts", "status": "error", "error": str(e)}

        # Step 6: PIL provisions
        yield {"step": "pil_provisions", "status": "in_progress"}
        try:
            provisions_result = extract_pil_provisions(col_section_text, legal_system, jurisdiction)
            yield {
                "step": "pil_provisions",
                "status": "completed",
                "data": {
                    "pil_provisions": provisions_result.pil_provisions,
                    "confidence": provisions_result.confidence,
                },
            }
        except Exception as e:
            logger.error("PIL provisions extraction failed: %s", str(e))
            yield {"step": "pil_provisions", "status": "error", "error": str(e)}

        # Step 7: COL issue
        yield {"step": "col_issue", "status": "in_progress"}
        try:
            issue_result = extract_col_issue(col_section_text, legal_system, jurisdiction)
            yield {
                "step": "col_issue",
                "status": "completed",
                "data": {
                    "choice_of_law_issue": issue_result.col_issue,
                    "confidence": issue_result.confidence,
                },
            }
        except Exception as e:
            logger.error("COL issue extraction failed: %s", str(e))
            yield {"step": "col_issue", "status": "error", "error": str(e)}

        # Step 8: Court's position
        yield {"step": "courts_position", "status": "in_progress"}
        try:
            position_result = extract_courts_position(col_section_text, legal_system, jurisdiction)
            yield {
                "step": "courts_position",
                "status": "completed",
                "data": {
                    "courts_position": position_result.courts_position,
                    "confidence": position_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Court's position extraction failed: %s", str(e))
            yield {"step": "courts_position", "status": "error", "error": str(e)}

        yield {"step": "analysis_complete", "status": "completed"}
