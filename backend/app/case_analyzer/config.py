"""Configuration for case analysis service."""

import logging

import openai
from agents import set_tracing_export_api_key

from app.config import config

logger = logging.getLogger(__name__)

_openai_client: openai.AsyncOpenAI | None = None
_tracing_configured = False


def get_openai_client() -> openai.AsyncOpenAI:
    """Get singleton AsyncOpenAI client for agents."""
    global _openai_client, _tracing_configured
    if not _tracing_configured:
        set_tracing_export_api_key(config.OPENAI_API_KEY or "")
        _tracing_configured = True
    if _openai_client is None:
        _openai_client = openai.AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3,
        )
    return _openai_client


# Task-specific model configuration
# gpt-5.4-nano: Fast, cheap, good for classification and simple extraction
# gpt-5.4-mini: Balanced, good for summarization and text generation
# gpt-5.6-terra: Balanced frontier reasoning for complex legal analysis
TASK_MODELS = {
    "abstract": "gpt-5.4-mini",
    "case_citation": "gpt-5.4-nano",
    "col_issue": "gpt-5.6-terra",
    "col_retrieval": "gpt-5.4-nano",
    "col_section": "gpt-5.6-terra",
    "courts_position": "gpt-5.6-terra",
    "dissenting_opinions": "gpt-5.6-terra",
    "jurisdiction_classification": "gpt-5.4-nano",
    "legal_system": "gpt-5.4-nano",
    "obiter_dicta": "gpt-5.6-terra",
    "pil_provisions": "gpt-5.4-nano",
    "relevant_facts": "gpt-5.4-mini",
    "themes": "gpt-5.4-nano",
}


def get_model(task: str) -> str:
    """Get the appropriate model for a specific task."""
    return TASK_MODELS.get(task, "gpt-5.4-nano")
