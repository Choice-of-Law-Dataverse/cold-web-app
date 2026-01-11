"""Configuration for case analysis service."""

import logging

import openai
from agents import set_tracing_export_api_key

from app.config import config

set_tracing_export_api_key(config.OPENAI_API_KEY if config.OPENAI_API_KEY is not None else "")

logger = logging.getLogger(__name__)

_openai_client = None


def get_openai_client():
    """Get singleton AsyncOpenAI client for agents."""
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


# Task-specific model configuration
# gpt-5-nano: Fast, cheap, good for classification and simple extraction
# gpt-5-mini: Balanced, good for summarization and text generation
# gpt-5.1: High reasoning capability, best for complex legal analysis
TASK_MODELS = {
    "abstract": "gpt-5-mini",
    "case_citation": "gpt-5-nano",
    "col_issue": "gpt-5.1",
    "col_section": "gpt-5-mini",
    "courts_position": "gpt-5.1",
    "dissenting_opinions": "gpt-5.1",
    "jurisdiction_classification": "gpt-5-nano",
    "legal_system": "gpt-5-nano",
    "obiter_dicta": "gpt-5.1",
    "pil_provisions": "gpt-5-nano",
    "relevant_facts": "gpt-5-mini",
    "themes": "gpt-5-nano",
}


def get_model(task: str) -> str:
    """Get the appropriate model for a specific task."""
    return TASK_MODELS.get(task, "gpt-4o-mini")
