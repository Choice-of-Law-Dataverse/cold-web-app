"""
Case analysis service using tools from cold-case-analysis repository.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, cast

import logfire

from app.case_analysis.models import (
    CaseCitationOutput,
    ColSectionOutput,
    JurisdictionOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
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

logger = logging.getLogger(__name__)


async def detect_jurisdiction(text: str) -> JurisdictionOutput:
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
        await detect_legal_system_type("", text)

        # Step 2: Classify precise jurisdiction
        jurisdiction_result = await detect_precise_jurisdiction_with_confidence(text)

        return jurisdiction_result


async def analyze_case_streaming(text: str, jurisdiction_data: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
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
        # Step 1: Extract COL sections (required for all subsequent steps)
        yield {"step": "col_extraction", "status": "in_progress"}

        try:
            col_result: ColSectionOutput = await extract_col_section(text, legal_system, jurisdiction)
            yield {
                "step": "col_extraction",
                "status": "completed",
                "data": {
                    "col_sections": col_result.col_sections,
                    "confidence": col_result.confidence,
                    "reasoning": col_result.reasoning,
                },
            }
            col_section_text = str(col_result)
        except BaseException as e:
            logger.error("COL extraction failed: %s", str(e))
            yield {"step": "col_extraction", "status": "error", "error": str(e)}
            return

        # Step 2-5: Run independent tasks in parallel (using gather for simpler error handling)
        yield {"step": "theme_classification", "status": "in_progress"}
        yield {"step": "case_citation", "status": "in_progress"}
        yield {"step": "relevant_facts", "status": "in_progress"}
        yield {"step": "pil_provisions", "status": "in_progress"}

        try:
            results = await asyncio.gather(
                theme_classification_node(text, col_section_text, legal_system, jurisdiction),
                extract_case_citation(text, legal_system, jurisdiction),
                extract_relevant_facts(text, col_result, legal_system, jurisdiction),
                extract_pil_provisions(text, col_result, legal_system, jurisdiction),
                return_exceptions=True,
            )

            theme_result_raw, citation_result_raw, facts_result_raw, provisions_result_raw = results

            # Check for exceptions and narrow types
            if isinstance(theme_result_raw, Exception):
                logger.error("Theme classification failed: %s", str(theme_result_raw))
                yield {"step": "theme_classification", "status": "error", "error": str(theme_result_raw)}
                return

            # Cast after exception check for type narrowing
            theme_result = cast(ThemeClassificationOutput, theme_result_raw)
            yield {
                "step": "theme_classification",
                "status": "completed",
                "data": {
                    "themes": theme_result.themes,
                    "confidence": theme_result.confidence,
                    "reasoning": theme_result.reasoning,
                },
            }

            if isinstance(citation_result_raw, Exception):
                logger.error("Case citation extraction failed: %s", str(citation_result_raw))
                yield {"step": "case_citation", "status": "error", "error": str(citation_result_raw)}
                citation_result = None
            else:
                # Cast after exception check for type narrowing
                citation_result = cast(CaseCitationOutput, citation_result_raw)
                yield {
                    "step": "case_citation",
                    "status": "completed",
                    "data": {
                        "case_citation": citation_result.case_citation,
                        "confidence": citation_result.confidence,
                    },
                }

            if isinstance(facts_result_raw, Exception):
                logger.error("Facts extraction failed: %s", str(facts_result_raw))
                yield {"step": "relevant_facts", "status": "error", "error": str(facts_result_raw)}
                return

            # Cast after exception check for type narrowing
            facts_result = cast(RelevantFactsOutput, facts_result_raw)
            yield {
                "step": "relevant_facts",
                "status": "completed",
                "data": {
                    "relevant_facts": facts_result.relevant_facts,
                    "confidence": facts_result.confidence,
                },
            }

            if isinstance(provisions_result_raw, Exception):
                logger.error("PIL provisions extraction failed: %s", str(provisions_result_raw))
                yield {"step": "pil_provisions", "status": "error", "error": str(provisions_result_raw)}
                return

            # Cast after exception check for type narrowing
            provisions_result = cast(PILProvisionsOutput, provisions_result_raw)
            yield {
                "step": "pil_provisions",
                "status": "completed",
                "data": {
                    "pil_provisions": provisions_result.pil_provisions,
                    "confidence": provisions_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Parallel task execution failed: %s", str(e))
            yield {"step": "parallel_tasks", "status": "error", "error": str(e)}
            return

        # Step 6: COL issue (depends on theme)
        yield {"step": "col_issue", "status": "in_progress"}
        try:
            issue_result = await extract_col_issue(text, col_result, legal_system, jurisdiction, theme_result)
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
            return

        # Step 7: Court's position (depends on theme and issue)
        yield {"step": "courts_position", "status": "in_progress"}
        try:
            position_task = asyncio.create_task(
                extract_courts_position(text, col_result, legal_system, jurisdiction, theme_result, issue_result)
            )
            position_result = await position_task
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
            return

        # Step 8: Abstract (requires all previous results)
        yield {"step": "abstract", "status": "in_progress"}
        try:
            abstract_task = asyncio.create_task(
                extract_abstract(
                    text,
                    legal_system,
                    jurisdiction,
                    theme_result,
                    facts_result,
                    provisions_result,
                    issue_result,
                    position_result,
                )
            )
            abstract_result = await abstract_task
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

        yield {"step": "analysis_complete", "status": "completed"}
