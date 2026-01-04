"""Configuration for case analysis service."""

import logging

from app.config import config

logger = logging.getLogger(__name__)

_openai_client = None


def get_openai_client():
    """
    Get singleton OpenAI client for agents.

    Note: nest_asyncio.apply() is required because the openai-agents library
    uses asyncio.run() internally, which would fail in an already-running async
    context (like FastAPI). nest_asyncio patches asyncio to allow nested event loops.
    This is applied once when the client is first created.
    """
    global _openai_client
    if _openai_client is None:
        import nest_asyncio
        import openai

        nest_asyncio.apply()
        _openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


# Task-specific model configuration
TASK_MODELS = {
    "abstract": "gpt-4o-mini",
    "case_citation": "gpt-4o-mini",
    "col_issue": "gpt-4o",
    "col_section": "gpt-4o-mini",
    "courts_position": "gpt-4o",
    "dissenting_opinions": "gpt-4o",
    "jurisdiction_classification": "gpt-4o-mini",
    "legal_system": "gpt-4o-mini",
    "obiter_dicta": "gpt-4o",
    "pil_provisions": "gpt-4o-mini",
    "relevant_facts": "gpt-4o-mini",
    "themes": "gpt-4o-mini",
}


def get_model(task: str) -> str:
    """Get the appropriate model for a specific task."""
    return TASK_MODELS.get(task, "gpt-4o-mini")
