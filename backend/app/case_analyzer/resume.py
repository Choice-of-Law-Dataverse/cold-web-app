"""Helpers for /analyze re-run and resume handling of persisted analyzer data."""

import logging
from typing import Any

from pydantic import ValidationError

from .tools.models import JurisdictionOutput

logger = logging.getLogger(__name__)

ANALYSIS_STEP_KEYS = [
    "col_extraction",
    "theme_classification",
    "case_citation",
    "relevant_facts",
    "pil_provisions",
    "col_issue",
    "courts_position",
    "obiter_dicta",
    "dissenting_opinions",
    "abstract",
]


def load_cached_results(analyzer_data: dict[str, Any]) -> dict[str, Any] | None:
    """Build the cached_results mapping for analyze_case_streaming from persisted analyzer data.

    Unwraps legacy {"result": ...} envelopes and drops empty or non-analysis keys.
    Returns None when there is no analyzer data at all.
    """
    if not analyzer_data:
        return None
    cached: dict[str, Any] = {}
    for step_key in ANALYSIS_STEP_KEYS:
        step_result = analyzer_data.get(step_key)
        if not step_result:
            continue
        if isinstance(step_result, dict) and "result" in step_result:
            cached[step_key] = step_result["result"]
        else:
            cached[step_key] = step_result
    return cached


def jurisdiction_from_analyzer_data(analyzer_data: dict[str, Any]) -> JurisdictionOutput | None:
    """Reconstruct the persisted jurisdiction so a resume does not re-run detection.

    Strips the user_confirmed marker before validation. Returns None when the
    persisted payload is missing or invalid, in which case detection re-runs.
    """
    stored = analyzer_data.get("jurisdiction")
    if not isinstance(stored, dict):
        return None
    try:
        return JurisdictionOutput.model_validate({k: v for k, v in stored.items() if k != "user_confirmed"})
    except ValidationError:
        logger.warning("Persisted jurisdiction is invalid; re-running detection")
        return None
