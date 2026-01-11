"""
Case analysis service using tools from cold-case-analysis repository.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, cast

import logfire

from .tools import (
    CaseCitationOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    JurisdictionOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
    classify_themes,
    detect_precise_jurisdiction_with_confidence,
    extract_abstract,
    extract_case_citation,
    extract_col_issue,
    extract_col_section,
    extract_courts_position,
    extract_dissenting_opinions,
    extract_obiter_dicta,
    extract_pil_provisions,
    extract_relevant_facts,
)

logger = logging.getLogger(__name__)


def _requires_common_law_steps(legal_system: str | None, jurisdiction: str | None) -> bool:
    """Return True when obiter/dissent steps are required for a workflow."""
    if legal_system and legal_system.strip().lower() == "common-law jurisdiction":
        return True
    if jurisdiction and jurisdiction.strip().lower() == "india":
        return True
    return False


async def detect_jurisdiction(text: str) -> JurisdictionOutput:
    """
    Detect jurisdiction from court decision text.

    Uses detect_precise_jurisdiction_with_confidence which returns a complete
    JurisdictionOutput including legal_system_type, precise_jurisdiction,
    jurisdiction_code, confidence, and reasoning.

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

        # Classify precise jurisdiction (includes legal system type detection)
        jurisdiction_result = await detect_precise_jurisdiction_with_confidence(text)

        return jurisdiction_result


def _reconstruct_col_section(cached: dict[str, Any]) -> ColSectionOutput:
    """Reconstruct ColSectionOutput from cached data."""
    return ColSectionOutput(
        col_sections=cached.get("col_sections", []),
        confidence=cached.get("confidence", "medium"),
        reasoning=cached.get("reasoning", "Restored from cache"),
    )


def _reconstruct_theme_classification(cached: dict[str, Any]) -> ThemeClassificationOutput:
    """Reconstruct ThemeClassificationOutput from cached data."""
    return ThemeClassificationOutput(
        themes=cached.get("themes", []),
        confidence=cached.get("confidence", "medium"),
        reasoning=cached.get("reasoning", "Restored from cache"),
    )


def _reconstruct_col_issue(cached: dict[str, Any]) -> Any:
    """Reconstruct ColIssueOutput from cached data."""
    from .tools.models import ColIssueOutput

    return ColIssueOutput(
        col_issue=cached.get("col_issue", ""),
        confidence=cached.get("confidence", "medium"),
        reasoning=cached.get("reasoning", "Restored from cache"),
    )


async def analyze_case_streaming(
    text: str,
    jurisdiction_data: dict[str, Any],
    cached_results: dict[str, Any] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Execute complete case analysis workflow with streaming updates.

    Yields intermediate results as they complete. If cached_results is provided,
    steps with cached data are skipped and their cached results are yielded immediately.

    Args:
        text: Full court decision text
        jurisdiction_data: Dictionary containing jurisdiction information
        cached_results: Optional dict of previously completed step results (for resume)

    Yields:
        Dictionary with step name, status, and data for each analysis step
    """
    legal_system = jurisdiction_data["legal_system_type"]
    jurisdiction = jurisdiction_data["precise_jurisdiction"]
    run_common_law_branches = _requires_common_law_steps(legal_system, jurisdiction)
    cached = cached_results or {}

    with logfire.span("case_analysis_workflow", resume=bool(cached_results)):
        # Step 1: Extract COL sections (required for all subsequent steps)
        if "col_extraction" in cached and cached["col_extraction"].get("col_sections"):
            col_result = _reconstruct_col_section(cached["col_extraction"])
            yield {"step": "col_extraction", "status": "completed", "data": cached["col_extraction"]}
            col_section_text = str(col_result)
        else:
            yield {"step": "col_extraction", "status": "in_progress"}
            try:
                col_result = await extract_col_section(text, legal_system, jurisdiction)
                yield {
                    "step": "col_extraction",
                    "status": "completed",
                    "data": col_result.model_dump(),
                }
                col_section_text = str(col_result)
            except Exception as e:
                logger.error("COL extraction failed: %s", str(e))
                yield {"step": "col_extraction", "status": "error", "error": str(e)}
                return

        # Step 2-5: Run independent tasks in parallel (or use cached)
        # Check which steps need to run
        need_theme = "theme_classification" not in cached or not cached["theme_classification"].get("themes")
        need_citation = "case_citation" not in cached or not cached["case_citation"].get("case_citation")
        need_facts = "relevant_facts" not in cached or not cached["relevant_facts"].get("relevant_facts")
        need_provisions = "pil_provisions" not in cached or not cached["pil_provisions"].get("pil_provisions")

        # Initialize results from cache or None
        theme_result: ThemeClassificationOutput | None = None
        citation_result: CaseCitationOutput | None = None
        facts_result: RelevantFactsOutput | None = None
        provisions_result: PILProvisionsOutput | None = None

        # Yield cached results immediately
        if not need_theme:
            theme_result = _reconstruct_theme_classification(cached["theme_classification"])
            yield {"step": "theme_classification", "status": "completed", "data": cached["theme_classification"]}
        else:
            yield {"step": "theme_classification", "status": "in_progress"}

        if not need_citation:
            citation_result = CaseCitationOutput(
                case_citation=cached["case_citation"].get("case_citation", ""),
                confidence=cached["case_citation"].get("confidence", "medium"),
                reasoning=cached["case_citation"].get("reasoning", "Restored from cache"),
            )
            yield {"step": "case_citation", "status": "completed", "data": cached["case_citation"]}
        else:
            yield {"step": "case_citation", "status": "in_progress"}

        if not need_facts:
            facts_result = RelevantFactsOutput(
                relevant_facts=cached["relevant_facts"].get("relevant_facts", ""),
                confidence=cached["relevant_facts"].get("confidence", "medium"),
                reasoning=cached["relevant_facts"].get("reasoning", "Restored from cache"),
            )
            yield {"step": "relevant_facts", "status": "completed", "data": cached["relevant_facts"]}
        else:
            yield {"step": "relevant_facts", "status": "in_progress"}

        if not need_provisions:
            provisions_result = PILProvisionsOutput(
                pil_provisions=cached["pil_provisions"].get("pil_provisions", []),
                confidence=cached["pil_provisions"].get("confidence", "medium"),
                reasoning=cached["pil_provisions"].get("reasoning", "Restored from cache"),
            )
            yield {"step": "pil_provisions", "status": "completed", "data": cached["pil_provisions"]}
        else:
            yield {"step": "pil_provisions", "status": "in_progress"}

        # Run only the steps that need to run
        if need_theme or need_citation or need_facts or need_provisions:
            try:
                tasks_to_run = []
                task_names = []

                if need_theme:
                    tasks_to_run.append(classify_themes(text, col_section_text, legal_system, jurisdiction))
                    task_names.append("theme_classification")
                if need_citation:
                    tasks_to_run.append(extract_case_citation(text, legal_system, jurisdiction))
                    task_names.append("case_citation")
                if need_facts:
                    tasks_to_run.append(extract_relevant_facts(text, col_result, legal_system, jurisdiction))
                    task_names.append("relevant_facts")
                if need_provisions:
                    tasks_to_run.append(extract_pil_provisions(text, col_result, legal_system, jurisdiction))
                    task_names.append("pil_provisions")

                results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

                for task_name, result in zip(task_names, results, strict=True):
                    if isinstance(result, Exception):
                        logger.error("%s failed: %s", task_name, str(result))
                        yield {"step": task_name, "status": "error", "error": str(result)}
                        if task_name in ("theme_classification", "relevant_facts", "pil_provisions"):
                            return  # Critical steps
                        continue

                    if task_name == "theme_classification":
                        theme_result = cast(ThemeClassificationOutput, result)
                        yield {"step": "theme_classification", "status": "completed", "data": theme_result.model_dump()}
                    elif task_name == "case_citation":
                        citation_result = cast(CaseCitationOutput, result)
                        yield {"step": "case_citation", "status": "completed", "data": citation_result.model_dump()}
                    elif task_name == "relevant_facts":
                        facts_result = cast(RelevantFactsOutput, result)
                        yield {"step": "relevant_facts", "status": "completed", "data": facts_result.model_dump()}
                    elif task_name == "pil_provisions":
                        provisions_result = cast(PILProvisionsOutput, result)
                        yield {"step": "pil_provisions", "status": "completed", "data": provisions_result.model_dump()}

            except Exception as e:
                logger.error("Parallel task execution failed: %s", str(e))
                yield {"step": "parallel_tasks", "status": "error", "error": str(e)}
                return

        # Verify we have required results
        if theme_result is None or facts_result is None or provisions_result is None:
            logger.error("Missing required results after parallel execution")
            yield {"step": "parallel_tasks", "status": "error", "error": "Missing required analysis results"}
            return

        # Step 6: COL issue (depends on theme)
        if "col_issue" in cached and cached["col_issue"].get("col_issue"):
            issue_result = _reconstruct_col_issue(cached["col_issue"])
            yield {"step": "col_issue", "status": "completed", "data": cached["col_issue"]}
        else:
            yield {"step": "col_issue", "status": "in_progress"}
            try:
                issue_result = await extract_col_issue(text, col_result, legal_system, jurisdiction, theme_result)
                yield {
                    "step": "col_issue",
                    "status": "completed",
                    "data": issue_result.model_dump(),
                }
            except Exception as e:
                logger.error("COL issue extraction failed: %s", str(e))
                yield {"step": "col_issue", "status": "error", "error": str(e)}
                return

        # Step 7: Court's position + Common Law extras (depends on theme and issue)
        obiter_result: ObiterDictaOutput | None = None
        dissent_result: DissentingOpinionsOutput | None = None
        position_result: CourtsPositionOutput | None = None

        # Check cache for these steps
        need_position = "courts_position" not in cached or not cached["courts_position"].get("courts_position")
        need_obiter = run_common_law_branches and (
            "obiter_dicta" not in cached or not cached["obiter_dicta"].get("obiter_dicta")
        )
        need_dissent = run_common_law_branches and (
            "dissenting_opinions" not in cached or not cached["dissenting_opinions"].get("dissenting_opinions")
        )

        # Yield cached results
        if not need_position:
            position_result = CourtsPositionOutput(
                courts_position=cached["courts_position"].get("courts_position", ""),
                confidence=cached["courts_position"].get("confidence", "medium"),
                reasoning=cached["courts_position"].get("reasoning", "Restored from cache"),
            )
            yield {"step": "courts_position", "status": "completed", "data": cached["courts_position"]}
        else:
            yield {"step": "courts_position", "status": "in_progress"}

        if run_common_law_branches:
            if not need_obiter:
                obiter_result = ObiterDictaOutput(
                    obiter_dicta=cached["obiter_dicta"].get("obiter_dicta", ""),
                    confidence=cached["obiter_dicta"].get("confidence", "medium"),
                    reasoning=cached["obiter_dicta"].get("reasoning", "Restored from cache"),
                )
                yield {"step": "obiter_dicta", "status": "completed", "data": cached["obiter_dicta"]}
            else:
                yield {"step": "obiter_dicta", "status": "in_progress"}

            if not need_dissent:
                dissent_result = DissentingOpinionsOutput(
                    dissenting_opinions=cached["dissenting_opinions"].get("dissenting_opinions", ""),
                    confidence=cached["dissenting_opinions"].get("confidence", "medium"),
                    reasoning=cached["dissenting_opinions"].get("reasoning", "Restored from cache"),
                )
                yield {"step": "dissenting_opinions", "status": "completed", "data": cached["dissenting_opinions"]}
            else:
                yield {"step": "dissenting_opinions", "status": "in_progress"}

        # Run only steps that need to run
        if need_position or need_obiter or need_dissent:
            tasks: list[tuple[str, asyncio.Task[Any]]] = []

            if need_position:
                tasks.append(
                    (
                        "courts_position",
                        asyncio.create_task(
                            extract_courts_position(text, col_result, legal_system, jurisdiction, theme_result, issue_result)
                        ),
                    )
                )

            if need_obiter:
                tasks.append(
                    (
                        "obiter_dicta",
                        asyncio.create_task(
                            extract_obiter_dicta(text, col_result, legal_system, jurisdiction, theme_result, issue_result)
                        ),
                    )
                )

            if need_dissent:
                tasks.append(
                    (
                        "dissenting_opinions",
                        asyncio.create_task(
                            extract_dissenting_opinions(
                                text, col_result, legal_system, jurisdiction, theme_result, issue_result
                            )
                        ),
                    )
                )

            try:
                results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
            except Exception as e:
                logger.error("Parallel analysis steps failed: %s", str(e))
                yield {"step": "courts_position", "status": "error", "error": str(e)}
                return

            for (step_name, _), result in zip(tasks, results, strict=True):
                if isinstance(result, Exception):
                    logger.error("%s extraction failed: %s", step_name, str(result))
                    yield {"step": step_name, "status": "error", "error": str(result)}
                    return

                if step_name == "courts_position":
                    position_result = cast(CourtsPositionOutput, result)
                    yield {"step": "courts_position", "status": "completed", "data": position_result.model_dump()}
                elif step_name == "obiter_dicta":
                    obiter_result = cast(ObiterDictaOutput, result)
                    yield {"step": "obiter_dicta", "status": "completed", "data": obiter_result.model_dump()}
                elif step_name == "dissenting_opinions":
                    dissent_result = cast(DissentingOpinionsOutput, result)
                    yield {"step": "dissenting_opinions", "status": "completed", "data": dissent_result.model_dump()}

        if position_result is None:
            error_msg = "Court's position extraction returned no result"
            logger.error(error_msg)
            yield {"step": "courts_position", "status": "error", "error": error_msg}
            return

        # Step 8: Abstract (requires all previous results)
        if "abstract" in cached and cached["abstract"].get("abstract"):
            yield {"step": "abstract", "status": "completed", "data": cached["abstract"]}
        else:
            yield {"step": "abstract", "status": "in_progress"}
            try:
                abstract_result = await extract_abstract(
                    text=text,
                    legal_system=legal_system,
                    jurisdiction=jurisdiction,
                    themes_output=theme_result,
                    facts_output=facts_result,
                    pil_provisions_output=provisions_result,
                    col_issue_output=issue_result,
                    court_position_output=position_result,
                    obiter_dicta_output=obiter_result,
                    dissenting_opinions_output=dissent_result,
                )
                yield {"step": "abstract", "status": "completed", "data": abstract_result.model_dump()}
            except Exception as e:
                logger.error("Abstract generation failed: %s", str(e))
                yield {"step": "abstract", "status": "error", "error": str(e)}

        yield {"step": "analysis_complete", "status": "completed"}
