"""Identity of the case analysis steps shared by the service, resume handling and the SSE route."""

from enum import StrEnum


class AnalysisStep(StrEnum):
    """Step names emitted on the analysis stream. Values are the wire-level SSE `step` strings."""

    JURISDICTION_DETECTION = "jurisdiction_detection"
    COL_EXTRACTION = "col_extraction"
    THEME_CLASSIFICATION = "theme_classification"
    CASE_CITATION = "case_citation"
    RELEVANT_FACTS = "relevant_facts"
    PIL_PROVISIONS = "pil_provisions"
    PARALLEL_TASKS = "parallel_tasks"
    COL_ISSUE = "col_issue"
    COURTS_POSITION = "courts_position"
    OBITER_DICTA = "obiter_dicta"
    DISSENTING_OPINIONS = "dissenting_opinions"
    ABSTRACT = "abstract"
    ANALYSIS_COMPLETE = "analysis_complete"


CACHEABLE_STEPS: tuple[AnalysisStep, ...] = (
    AnalysisStep.COL_EXTRACTION,
    AnalysisStep.THEME_CLASSIFICATION,
    AnalysisStep.CASE_CITATION,
    AnalysisStep.RELEVANT_FACTS,
    AnalysisStep.PIL_PROVISIONS,
    AnalysisStep.COL_ISSUE,
    AnalysisStep.COURTS_POSITION,
    AnalysisStep.OBITER_DICTA,
    AnalysisStep.DISSENTING_OPINIONS,
    AnalysisStep.ABSTRACT,
)

NON_ABORTING_STEPS: frozenset[AnalysisStep] = frozenset({AnalysisStep.CASE_CITATION})
"""Parallel-stage steps whose failure emits an error event but lets the run continue; any other failure ends it."""

_PERSISTED_KEYS: dict[str, str] = {AnalysisStep.JURISDICTION_DETECTION: "jurisdiction"}


def persisted_key(step: str) -> str:
    """Return the analyzer_data key a step's result is stored under."""
    return _PERSISTED_KEYS.get(step, str(step))
