"""
Case analysis service using tools from cold-case-analysis repository.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, cast

import logfire

from .consistency_checker import check_consistency
from .runner import retry_with_feedback
from .tools import (
    CaseCitationOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    JurisdictionOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    StepResult,
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
from .tools.models import ColIssueOutput

logger = logging.getLogger(__name__)

STEP_OUTPUT_TYPES: dict[str, type[Any]] = {
    "theme_classification": ThemeClassificationOutput,
    "relevant_facts": RelevantFactsOutput,
    "pil_provisions": PILProvisionsOutput,
    "col_issue": ColIssueOutput,
    "courts_position": CourtsPositionOutput,
    "obiter_dicta": ObiterDictaOutput,
    "dissenting_opinions": DissentingOpinionsOutput,
}


def _requires_common_law_steps(legal_system: str | None, jurisdiction: str | None) -> bool:
    if legal_system and legal_system.strip().lower() == "common-law jurisdiction":
        return True
    if jurisdiction and jurisdiction.strip().lower() == "india":
        return True
    return False


async def detect_jurisdiction(text: str) -> JurisdictionOutput:
    with logfire.span("jurisdiction_detection"):
        if not text or len(text.strip()) < 50:
            return JurisdictionOutput(
                legal_system_type="No court decision",
                precise_jurisdiction="Unknown",
                jurisdiction_code="XX",
                confidence="low",
                reasoning="Text too short for analysis",
            )

        jurisdiction_result = await detect_precise_jurisdiction_with_confidence(text)

        return jurisdiction_result


def _reconstruct_col_section(cached: dict[str, Any]) -> ColSectionOutput:
    return ColSectionOutput(
        col_sections=cached.get("col_sections", []),
        confidence=cached.get("confidence", "medium"),
        reasoning=cached.get("reasoning", "Restored from cache"),
    )


def _reconstruct_theme_classification(cached: dict[str, Any]) -> ThemeClassificationOutput:
    return ThemeClassificationOutput(
        themes=cached.get("themes", []),
        confidence=cached.get("confidence", "medium"),
        reasoning=cached.get("reasoning", "Restored from cache"),
    )


def _reconstruct_col_issue(cached: dict[str, Any]) -> ColIssueOutput:
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
    legal_system = jurisdiction_data["legal_system_type"]
    jurisdiction = jurisdiction_data["precise_jurisdiction"]
    run_common_law_branches = _requires_common_law_steps(legal_system, jurisdiction)
    cached = cached_results or {}
    last_response_id: str | None = None
    response_ids: dict[str, str | None] = {}

    with logfire.span("case_analysis_workflow", resume=bool(cached_results)):
        if "col_extraction" in cached and cached["col_extraction"].get("col_sections"):
            col_result = _reconstruct_col_section(cached["col_extraction"])
            yield {"step": "col_extraction", "status": "completed", "data": cached["col_extraction"]}
            col_section_text = str(col_result)
        else:
            yield {"step": "col_extraction", "status": "in_progress"}
            try:
                col_step = await extract_col_section(text, legal_system, jurisdiction)
                col_result = col_step.output
                last_response_id = col_step.response_id
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

        need_theme = "theme_classification" not in cached or not cached["theme_classification"].get("themes")
        need_citation = "case_citation" not in cached or not cached["case_citation"].get("case_citation")
        need_facts = "relevant_facts" not in cached or not cached["relevant_facts"].get("relevant_facts")
        need_provisions = "pil_provisions" not in cached or not cached["pil_provisions"].get("pil_provisions")

        theme_result: ThemeClassificationOutput | None = None
        citation_result: CaseCitationOutput | None = None
        facts_result: RelevantFactsOutput | None = None
        provisions_result: PILProvisionsOutput | None = None

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

        if need_theme or need_citation or need_facts or need_provisions:
            try:
                tasks_to_run = []
                task_names = []

                if need_theme:
                    tasks_to_run.append(
                        classify_themes(
                            text, col_section_text, legal_system, jurisdiction, previous_response_id=last_response_id
                        )
                    )
                    task_names.append("theme_classification")
                if need_citation:
                    tasks_to_run.append(
                        extract_case_citation(text, legal_system, jurisdiction, previous_response_id=last_response_id)
                    )
                    task_names.append("case_citation")
                if need_facts:
                    tasks_to_run.append(
                        extract_relevant_facts(
                            text, col_result, legal_system, jurisdiction, previous_response_id=last_response_id
                        )
                    )
                    task_names.append("relevant_facts")
                if need_provisions:
                    tasks_to_run.append(
                        extract_pil_provisions(
                            text, col_result, legal_system, jurisdiction, previous_response_id=last_response_id
                        )
                    )
                    task_names.append("pil_provisions")

                results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

                for task_name, result in zip(task_names, results, strict=True):
                    if isinstance(result, Exception):
                        logger.error("%s failed: %s", task_name, str(result))
                        yield {"step": task_name, "status": "error", "error": str(result)}
                        if task_name in ("theme_classification", "relevant_facts", "pil_provisions"):
                            return
                        continue

                    step = cast(StepResult[Any], result)
                    response_ids[task_name] = step.response_id

                    if task_name == "theme_classification":
                        theme_result = cast(ThemeClassificationOutput, step.output)
                        last_response_id = step.response_id
                        yield {"step": "theme_classification", "status": "completed", "data": theme_result.model_dump()}
                    elif task_name == "case_citation":
                        citation_result = cast(CaseCitationOutput, step.output)
                        yield {"step": "case_citation", "status": "completed", "data": citation_result.model_dump()}
                    elif task_name == "relevant_facts":
                        facts_result = cast(RelevantFactsOutput, step.output)
                        yield {"step": "relevant_facts", "status": "completed", "data": facts_result.model_dump()}
                    elif task_name == "pil_provisions":
                        provisions_result = cast(PILProvisionsOutput, step.output)
                        yield {"step": "pil_provisions", "status": "completed", "data": provisions_result.model_dump()}

            except Exception as e:
                logger.error("Parallel task execution failed: %s", str(e))
                yield {"step": "parallel_tasks", "status": "error", "error": str(e)}
                return

        if theme_result is None or facts_result is None or provisions_result is None:
            logger.error("Missing required results after parallel execution")
            yield {"step": "parallel_tasks", "status": "error", "error": "Missing required analysis results"}
            return

        if "col_issue" in cached and cached["col_issue"].get("col_issue"):
            issue_result = _reconstruct_col_issue(cached["col_issue"])
            yield {"step": "col_issue", "status": "completed", "data": cached["col_issue"]}
        else:
            yield {"step": "col_issue", "status": "in_progress"}
            try:
                issue_step = await extract_col_issue(
                    text,
                    col_result,
                    legal_system,
                    jurisdiction,
                    theme_result,
                    previous_response_id=last_response_id,
                )
                issue_result = issue_step.output
                last_response_id = issue_step.response_id
                response_ids["col_issue"] = issue_step.response_id
                yield {
                    "step": "col_issue",
                    "status": "completed",
                    "data": issue_result.model_dump(),
                }
            except Exception as e:
                logger.error("COL issue extraction failed: %s", str(e))
                yield {"step": "col_issue", "status": "error", "error": str(e)}
                return

        obiter_result: ObiterDictaOutput | None = None
        dissent_result: DissentingOpinionsOutput | None = None
        position_result: CourtsPositionOutput | None = None

        need_position = "courts_position" not in cached or not cached["courts_position"].get("courts_position")
        need_obiter = run_common_law_branches and (
            "obiter_dicta" not in cached or not cached["obiter_dicta"].get("obiter_dicta")
        )
        need_dissent = run_common_law_branches and (
            "dissenting_opinions" not in cached or not cached["dissenting_opinions"].get("dissenting_opinions")
        )

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

        if need_position or need_obiter or need_dissent:
            tasks: list[tuple[str, asyncio.Task[Any]]] = []

            if need_position:
                tasks.append(
                    (
                        "courts_position",
                        asyncio.create_task(
                            extract_courts_position(
                                text,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                                previous_response_id=last_response_id,
                            )
                        ),
                    )
                )

            if need_obiter:
                tasks.append(
                    (
                        "obiter_dicta",
                        asyncio.create_task(
                            extract_obiter_dicta(
                                text,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                                previous_response_id=last_response_id,
                            )
                        ),
                    )
                )

            if need_dissent:
                tasks.append(
                    (
                        "dissenting_opinions",
                        asyncio.create_task(
                            extract_dissenting_opinions(
                                text,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                                previous_response_id=last_response_id,
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

                step = cast(StepResult[Any], result)
                response_ids[step_name] = step.response_id

                if step_name == "courts_position":
                    position_result = cast(CourtsPositionOutput, step.output)
                    last_response_id = step.response_id
                    yield {"step": "courts_position", "status": "completed", "data": position_result.model_dump()}
                elif step_name == "obiter_dicta":
                    obiter_result = cast(ObiterDictaOutput, step.output)
                    yield {"step": "obiter_dicta", "status": "completed", "data": obiter_result.model_dump()}
                elif step_name == "dissenting_opinions":
                    dissent_result = cast(DissentingOpinionsOutput, step.output)
                    yield {"step": "dissenting_opinions", "status": "completed", "data": dissent_result.model_dump()}

        if position_result is None:
            error_msg = "Court's position extraction returned no result"
            logger.error(error_msg)
            yield {"step": "courts_position", "status": "error", "error": error_msg}
            return

        yield {"step": "consistency_check", "status": "in_progress"}
        consistency_result = await check_consistency(
            themes_output=theme_result,
            facts_output=facts_result,
            provisions_output=provisions_result,
            col_issue_output=issue_result,
            position_output=position_result,
            obiter_output=obiter_result,
            dissent_output=dissent_result,
            previous_response_id=last_response_id,
        )

        high_severity_issues = [i for i in consistency_result.issues if i.severity == "high"]
        if high_severity_issues:
            yield {
                "step": "consistency_check",
                "status": "completed",
                "data": {"is_consistent": False, "retrying_steps": [i.step for i in high_severity_issues]},
            }

            for issue in high_severity_issues:
                rid = response_ids.get(issue.step)
                if rid is None:
                    logger.warning("No response_id for %s, skipping consistency retry", issue.step)
                    continue

                output_type = STEP_OUTPUT_TYPES.get(issue.step)
                if output_type is None:
                    continue

                correction = f"Consistency issue detected: {issue.description}. Please re-analyze and correct this step."
                try:
                    retry_step = await retry_with_feedback(issue.step, output_type, correction, rid)
                    response_ids[issue.step] = retry_step.response_id

                    if issue.step == "theme_classification":
                        theme_result = cast(ThemeClassificationOutput, retry_step.output)
                        yield {"step": "theme_classification", "status": "completed", "data": theme_result.model_dump()}
                    elif issue.step == "relevant_facts":
                        facts_result = cast(RelevantFactsOutput, retry_step.output)
                        yield {"step": "relevant_facts", "status": "completed", "data": facts_result.model_dump()}
                    elif issue.step == "pil_provisions":
                        provisions_result = cast(PILProvisionsOutput, retry_step.output)
                        yield {"step": "pil_provisions", "status": "completed", "data": provisions_result.model_dump()}
                    elif issue.step == "col_issue":
                        issue_result = cast(ColIssueOutput, retry_step.output)
                        yield {"step": "col_issue", "status": "completed", "data": issue_result.model_dump()}
                    elif issue.step == "courts_position":
                        position_result = cast(CourtsPositionOutput, retry_step.output)
                        last_response_id = retry_step.response_id
                        yield {"step": "courts_position", "status": "completed", "data": position_result.model_dump()}
                    elif issue.step == "obiter_dicta":
                        obiter_result = cast(ObiterDictaOutput, retry_step.output)
                        yield {"step": "obiter_dicta", "status": "completed", "data": obiter_result.model_dump()}
                    elif issue.step == "dissenting_opinions":
                        dissent_result = cast(DissentingOpinionsOutput, retry_step.output)
                        yield {"step": "dissenting_opinions", "status": "completed", "data": dissent_result.model_dump()}
                except Exception as e:
                    logger.error("Consistency retry for %s failed: %s", issue.step, e)
        else:
            yield {"step": "consistency_check", "status": "completed", "data": {"is_consistent": True}}

        if "abstract" in cached and cached["abstract"].get("abstract"):
            yield {"step": "abstract", "status": "completed", "data": cached["abstract"]}
        else:
            yield {"step": "abstract", "status": "in_progress"}
            try:
                abstract_step = await extract_abstract(
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
                    previous_response_id=last_response_id,
                )
                yield {"step": "abstract", "status": "completed", "data": abstract_step.output.model_dump()}
            except Exception as e:
                logger.error("Abstract generation failed: %s", str(e))
                yield {"step": "abstract", "status": "error", "error": str(e)}

        yield {"step": "analysis_complete", "status": "completed"}
