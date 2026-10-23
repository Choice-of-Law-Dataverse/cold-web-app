"""
Case analysis service using tools from cold-case-analysis repository.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, cast

import logfire
from pydantic import BaseModel

from .steps import NON_ABORTING_STEPS, AnalysisStep
from .tools import (
    AbstractOutput,
    CaseCitationOutput,
    ColIssueOutput,
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
from .tools.document_nav import DocumentContext
from .utils.legal_system import requires_common_law_steps
from .validation import (
    ValidatorFn,
    validate_abstract,
    validate_case_citation,
    validate_col_issue,
    validate_col_section_content,
    validate_col_section_provenance,
    validate_courts_position,
    validate_dissenting_opinions,
    validate_obiter_dicta,
    validate_pil_provisions,
    validate_relevant_facts,
    validate_themes,
)

logger = logging.getLogger(__name__)

_EVIDENCE_KEY = "_evidence"
_NAVIGATION_TOOLS_KEY = "navigation_tools"
_POLICY_VERSION_KEY = "policy_version"
_EVIDENCE_POLICY_VERSION = 9


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


def _restore_from_cache[ModelT: BaseModel](
    model_cls: type[ModelT],
    cached: dict[str, Any],
    field: str,
    default: Any,
) -> ModelT:
    return model_cls.model_validate(
        {
            **cached,
            field: cached.get(field, default),
            "confidence": cached.get("confidence", "medium"),
            "reasoning": cached.get("reasoning", "Restored from cache"),
        }
    )


def _step_data(step: StepResult[Any]) -> dict[str, Any]:
    if not isinstance(step.output, BaseModel):
        raise TypeError("Case analyzer step output must be a Pydantic model")
    return {
        **step.output.model_dump(),
        _EVIDENCE_KEY: {
            **step.evidence,
            _NAVIGATION_TOOLS_KEY: list(step.tool_names),
            _POLICY_VERSION_KEY: _EVIDENCE_POLICY_VERSION,
        },
    }


def _cached_tool_names(cached_step: dict[str, Any]) -> frozenset[str]:
    evidence = cached_step.get(_EVIDENCE_KEY)
    if not isinstance(evidence, dict):
        return frozenset()
    names = evidence.get(_NAVIGATION_TOOLS_KEY)
    if not isinstance(names, list):
        return frozenset()
    return frozenset(name for name in names if isinstance(name, str))


def _cache_is_valid[ModelT: BaseModel](
    cached: dict[str, Any],
    step_name: AnalysisStep,
    model_cls: type[ModelT],
    field: str,
    default: Any,
    validator: ValidatorFn,
) -> bool:
    cached_step = cached.get(step_name)
    if not isinstance(cached_step, dict):
        return False
    try:
        output = _restore_from_cache(model_cls, cached_step, field, default)
    except Exception:
        logger.info("Discarding invalid cached %s payload", step_name)
        return False
    evidence = cached_step.get(_EVIDENCE_KEY)
    policy_version = evidence.get(_POLICY_VERSION_KEY) if isinstance(evidence, dict) else None
    if (policy_version is not None or step_name in {AnalysisStep.CASE_CITATION, AnalysisStep.COL_EXTRACTION}) and (
        policy_version != _EVIDENCE_POLICY_VERSION
    ):
        logger.info("Re-running cached %s from an older analysis policy", step_name)
        return False
    validation_error = validator(output, _cached_tool_names(cached_step))
    if validation_error:
        logger.info("Re-running cached %s step: %s", step_name, validation_error)
        return False
    return True


async def analyze_case_streaming(
    text: str,
    cached_results: dict[str, Any] | None = None,
    draft_id: int = 0,
    jurisdiction_override: JurisdictionOutput | None = None,
    file_name: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Execute complete case analysis workflow with streaming updates.

    Runs jurisdiction detection in parallel with col_section extraction as the
    first stage; the rest of the pipeline depends on the detected jurisdiction.
    Pass `jurisdiction_override` to skip detection and use a user-corrected value.
    Yields intermediate results as they complete. If cached_results is provided,
    steps with cached data are skipped and their cached results are yielded immediately.
    """
    cached = cached_results or {}
    doc_ctx = DocumentContext(draft_id=draft_id, text=text, file_name=file_name)

    with logfire.span("case_analysis_workflow", resume=bool(cached_results), draft_id=draft_id):
        # Stage 1: jurisdiction detection (or override) and col_section run concurrently.
        col_cached = _cache_is_valid(
            cached,
            AnalysisStep.COL_EXTRACTION,
            ColSectionOutput,
            "col_sections",
            [],
            validate_col_section_content,
        )
        if col_cached:
            cached_col = _restore_from_cache(ColSectionOutput, cached[AnalysisStep.COL_EXTRACTION], "col_sections", [])
            provenance_error = validate_col_section_provenance(
                cached_col,
                cached[AnalysisStep.COL_EXTRACTION].get(_EVIDENCE_KEY),
                doc_ctx.paragraphs,
            )
            if provenance_error is not None:
                logger.info("Re-running cached col_extraction step: %s", provenance_error)
                col_cached = False

        if jurisdiction_override is None:
            yield {"step": AnalysisStep.JURISDICTION_DETECTION, "status": "in_progress"}
        if not col_cached:
            yield {"step": AnalysisStep.COL_EXTRACTION, "status": "in_progress"}

        jurisdiction_task = asyncio.create_task(detect_jurisdiction(text)) if jurisdiction_override is None else None
        col_task = asyncio.create_task(extract_col_section(doc_ctx)) if not col_cached else None

        if jurisdiction_task is not None:
            try:
                jurisdiction_data = await jurisdiction_task
                yield {
                    "step": AnalysisStep.JURISDICTION_DETECTION,
                    "status": "completed",
                    "data": jurisdiction_data.model_dump(),
                }
            except Exception as e:
                logger.error("Jurisdiction detection failed: %s", str(e))
                yield {"step": AnalysisStep.JURISDICTION_DETECTION, "status": "error", "error": str(e)}
                if col_task is not None:
                    col_task.cancel()
                return
        else:
            assert jurisdiction_override is not None
            jurisdiction_data = jurisdiction_override

        legal_system = jurisdiction_data.legal_system_type
        jurisdiction = jurisdiction_data.precise_jurisdiction
        run_common_law_branches = requires_common_law_steps(legal_system, jurisdiction)

        if col_task is not None:
            try:
                col_step = await col_task
                col_result = col_step.output
            except Exception as e:
                logger.error("COL extraction failed: %s", str(e))
                yield {"step": AnalysisStep.COL_EXTRACTION, "status": "error", "error": str(e)}
                return
            if not any(section.strip() for section in col_result.col_sections):
                logger.error("COL extraction returned no sections for draft %d", draft_id)
                yield {
                    "step": AnalysisStep.COL_EXTRACTION,
                    "status": "error",
                    "error": "No choice-of-law sections could be extracted from this document.",
                }
                return
            yield {
                "step": AnalysisStep.COL_EXTRACTION,
                "status": "completed",
                "data": _step_data(col_step),
            }
            col_section_text = str(col_result)
        else:
            col_result = _restore_from_cache(ColSectionOutput, cached[AnalysisStep.COL_EXTRACTION], "col_sections", [])
            yield {"step": AnalysisStep.COL_EXTRACTION, "status": "completed", "data": cached[AnalysisStep.COL_EXTRACTION]}
            col_section_text = str(col_result)

        need_theme = not _cache_is_valid(
            cached,
            AnalysisStep.THEME_CLASSIFICATION,
            ThemeClassificationOutput,
            "themes",
            [],
            validate_themes,
        )
        need_citation = not _cache_is_valid(
            cached,
            AnalysisStep.CASE_CITATION,
            CaseCitationOutput,
            "case_citation",
            "",
            validate_case_citation,
        )
        need_facts = not _cache_is_valid(
            cached,
            AnalysisStep.RELEVANT_FACTS,
            RelevantFactsOutput,
            "relevant_facts",
            "",
            validate_relevant_facts,
        )
        need_provisions = not _cache_is_valid(
            cached,
            AnalysisStep.PIL_PROVISIONS,
            PILProvisionsOutput,
            "pil_provisions",
            [],
            validate_pil_provisions,
        )

        theme_result: ThemeClassificationOutput | None = None
        facts_result: RelevantFactsOutput | None = None
        provisions_result: PILProvisionsOutput | None = None

        if not need_theme:
            theme_result = _restore_from_cache(
                ThemeClassificationOutput, cached[AnalysisStep.THEME_CLASSIFICATION], "themes", []
            )
            yield {
                "step": AnalysisStep.THEME_CLASSIFICATION,
                "status": "completed",
                "data": cached[AnalysisStep.THEME_CLASSIFICATION],
            }
        else:
            yield {"step": AnalysisStep.THEME_CLASSIFICATION, "status": "in_progress"}

        if not need_citation:
            yield {"step": AnalysisStep.CASE_CITATION, "status": "completed", "data": cached[AnalysisStep.CASE_CITATION]}
        else:
            yield {"step": AnalysisStep.CASE_CITATION, "status": "in_progress"}

        if not need_facts:
            facts_result = _restore_from_cache(RelevantFactsOutput, cached[AnalysisStep.RELEVANT_FACTS], "relevant_facts", "")
            yield {"step": AnalysisStep.RELEVANT_FACTS, "status": "completed", "data": cached[AnalysisStep.RELEVANT_FACTS]}
        else:
            yield {"step": AnalysisStep.RELEVANT_FACTS, "status": "in_progress"}

        if not need_provisions:
            provisions_result = _restore_from_cache(
                PILProvisionsOutput, cached[AnalysisStep.PIL_PROVISIONS], "pil_provisions", []
            )
            yield {"step": AnalysisStep.PIL_PROVISIONS, "status": "completed", "data": cached[AnalysisStep.PIL_PROVISIONS]}
        else:
            yield {"step": AnalysisStep.PIL_PROVISIONS, "status": "in_progress"}

        if need_theme or need_citation or need_facts or need_provisions:
            try:
                tasks_to_run = []
                task_names = []

                if need_theme:
                    tasks_to_run.append(classify_themes(doc_ctx, col_section_text, legal_system, jurisdiction))
                    task_names.append(AnalysisStep.THEME_CLASSIFICATION)
                if need_citation:
                    tasks_to_run.append(extract_case_citation(doc_ctx, legal_system, jurisdiction))
                    task_names.append(AnalysisStep.CASE_CITATION)
                if need_facts:
                    tasks_to_run.append(extract_relevant_facts(doc_ctx, col_result, legal_system, jurisdiction))
                    task_names.append(AnalysisStep.RELEVANT_FACTS)
                if need_provisions:
                    tasks_to_run.append(extract_pil_provisions(doc_ctx, col_result, legal_system, jurisdiction))
                    task_names.append(AnalysisStep.PIL_PROVISIONS)

                results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

                for task_name, result in zip(task_names, results, strict=True):
                    if isinstance(result, Exception):
                        logger.error("%s failed: %s", task_name, str(result))
                        yield {"step": task_name, "status": "error", "error": str(result)}
                        if task_name not in NON_ABORTING_STEPS:
                            return
                        continue

                    step = cast(StepResult[Any], result)

                    if task_name == AnalysisStep.THEME_CLASSIFICATION:
                        theme_result = cast(ThemeClassificationOutput, step.output)
                        yield {"step": AnalysisStep.THEME_CLASSIFICATION, "status": "completed", "data": _step_data(step)}
                    elif task_name == AnalysisStep.CASE_CITATION:
                        yield {"step": AnalysisStep.CASE_CITATION, "status": "completed", "data": _step_data(step)}
                    elif task_name == AnalysisStep.RELEVANT_FACTS:
                        facts_result = cast(RelevantFactsOutput, step.output)
                        yield {"step": AnalysisStep.RELEVANT_FACTS, "status": "completed", "data": _step_data(step)}
                    elif task_name == AnalysisStep.PIL_PROVISIONS:
                        provisions_result = cast(PILProvisionsOutput, step.output)
                        yield {"step": AnalysisStep.PIL_PROVISIONS, "status": "completed", "data": _step_data(step)}

            except Exception as e:
                logger.error("Parallel task execution failed: %s", str(e))
                yield {"step": AnalysisStep.PARALLEL_TASKS, "status": "error", "error": str(e)}
                return

        if theme_result is None or facts_result is None or provisions_result is None:
            logger.error("Missing required results after parallel execution")
            yield {"step": AnalysisStep.PARALLEL_TASKS, "status": "error", "error": "Missing required analysis results"}
            return

        issue_cached = _cache_is_valid(
            cached,
            AnalysisStep.COL_ISSUE,
            ColIssueOutput,
            "col_issue",
            "",
            validate_col_issue,
        )
        if issue_cached:
            issue_result = _restore_from_cache(ColIssueOutput, cached[AnalysisStep.COL_ISSUE], "col_issue", "")
            yield {"step": AnalysisStep.COL_ISSUE, "status": "completed", "data": cached[AnalysisStep.COL_ISSUE]}
        else:
            yield {"step": AnalysisStep.COL_ISSUE, "status": "in_progress"}
            try:
                issue_step = await extract_col_issue(
                    doc_ctx,
                    col_result,
                    legal_system,
                    jurisdiction,
                    theme_result,
                )
                issue_result = issue_step.output
                yield {
                    "step": AnalysisStep.COL_ISSUE,
                    "status": "completed",
                    "data": _step_data(issue_step),
                }
            except Exception as e:
                logger.error("COL issue extraction failed: %s", str(e))
                yield {"step": AnalysisStep.COL_ISSUE, "status": "error", "error": str(e)}
                return

        obiter_result: ObiterDictaOutput | None = None
        dissent_result: DissentingOpinionsOutput | None = None
        position_result: CourtsPositionOutput | None = None

        need_position = not _cache_is_valid(
            cached,
            AnalysisStep.COURTS_POSITION,
            CourtsPositionOutput,
            "courts_position",
            "",
            validate_courts_position,
        )
        need_obiter = run_common_law_branches and not _cache_is_valid(
            cached,
            AnalysisStep.OBITER_DICTA,
            ObiterDictaOutput,
            "obiter_dicta",
            "",
            validate_obiter_dicta,
        )
        need_dissent = run_common_law_branches and not _cache_is_valid(
            cached,
            AnalysisStep.DISSENTING_OPINIONS,
            DissentingOpinionsOutput,
            "dissenting_opinions",
            "",
            validate_dissenting_opinions,
        )

        if not need_position:
            position_result = _restore_from_cache(
                CourtsPositionOutput, cached[AnalysisStep.COURTS_POSITION], "courts_position", ""
            )
            yield {"step": AnalysisStep.COURTS_POSITION, "status": "completed", "data": cached[AnalysisStep.COURTS_POSITION]}
        else:
            yield {"step": AnalysisStep.COURTS_POSITION, "status": "in_progress"}

        if run_common_law_branches:
            if not need_obiter:
                obiter_result = _restore_from_cache(ObiterDictaOutput, cached[AnalysisStep.OBITER_DICTA], "obiter_dicta", "")
                yield {"step": AnalysisStep.OBITER_DICTA, "status": "completed", "data": cached[AnalysisStep.OBITER_DICTA]}
            else:
                yield {"step": AnalysisStep.OBITER_DICTA, "status": "in_progress"}

            if not need_dissent:
                dissent_result = _restore_from_cache(
                    DissentingOpinionsOutput, cached[AnalysisStep.DISSENTING_OPINIONS], "dissenting_opinions", ""
                )
                yield {
                    "step": AnalysisStep.DISSENTING_OPINIONS,
                    "status": "completed",
                    "data": cached[AnalysisStep.DISSENTING_OPINIONS],
                }
            else:
                yield {"step": AnalysisStep.DISSENTING_OPINIONS, "status": "in_progress"}

        if need_position or need_obiter or need_dissent:
            tasks: list[tuple[AnalysisStep, asyncio.Task[Any]]] = []

            if need_position:
                tasks.append(
                    (
                        AnalysisStep.COURTS_POSITION,
                        asyncio.create_task(
                            extract_courts_position(
                                doc_ctx,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                            )
                        ),
                    )
                )

            if need_obiter:
                tasks.append(
                    (
                        AnalysisStep.OBITER_DICTA,
                        asyncio.create_task(
                            extract_obiter_dicta(
                                doc_ctx,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                            )
                        ),
                    )
                )

            if need_dissent:
                tasks.append(
                    (
                        AnalysisStep.DISSENTING_OPINIONS,
                        asyncio.create_task(
                            extract_dissenting_opinions(
                                doc_ctx,
                                col_result,
                                legal_system,
                                jurisdiction,
                                theme_result,
                                issue_result,
                            )
                        ),
                    )
                )

            try:
                results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
            except Exception as e:
                logger.error("Parallel analysis steps failed: %s", str(e))
                yield {"step": AnalysisStep.COURTS_POSITION, "status": "error", "error": str(e)}
                return

            for (step_name, _), result in zip(tasks, results, strict=True):
                if isinstance(result, Exception):
                    logger.error("%s extraction failed: %s", step_name, str(result))
                    yield {"step": step_name, "status": "error", "error": str(result)}
                    return

                step = cast(StepResult[Any], result)

                if step_name == AnalysisStep.COURTS_POSITION:
                    position_result = cast(CourtsPositionOutput, step.output)
                    yield {"step": AnalysisStep.COURTS_POSITION, "status": "completed", "data": _step_data(step)}
                elif step_name == AnalysisStep.OBITER_DICTA:
                    obiter_result = cast(ObiterDictaOutput, step.output)
                    yield {"step": AnalysisStep.OBITER_DICTA, "status": "completed", "data": _step_data(step)}
                elif step_name == AnalysisStep.DISSENTING_OPINIONS:
                    dissent_result = cast(DissentingOpinionsOutput, step.output)
                    yield {"step": AnalysisStep.DISSENTING_OPINIONS, "status": "completed", "data": _step_data(step)}

        if position_result is None:
            error_msg = "Court's position extraction returned no result"
            logger.error(error_msg)
            yield {"step": AnalysisStep.COURTS_POSITION, "status": "error", "error": error_msg}
            return

        abstract_cached = _cache_is_valid(
            cached,
            AnalysisStep.ABSTRACT,
            AbstractOutput,
            "abstract",
            "",
            validate_abstract,
        )
        if abstract_cached:
            yield {"step": AnalysisStep.ABSTRACT, "status": "completed", "data": cached[AnalysisStep.ABSTRACT]}
        else:
            yield {"step": AnalysisStep.ABSTRACT, "status": "in_progress"}
            try:
                abstract_step = await extract_abstract(
                    doc_ctx,
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
                yield {"step": AnalysisStep.ABSTRACT, "status": "completed", "data": _step_data(abstract_step)}
            except Exception as e:
                logger.error("Abstract generation failed: %s", str(e))
                yield {"step": AnalysisStep.ABSTRACT, "status": "error", "error": str(e)}
                return

        yield {"step": AnalysisStep.ANALYSIS_COMPLETE, "status": "completed"}
