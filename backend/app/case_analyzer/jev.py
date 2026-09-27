"""TypeSafe Jev client for the case analyzer's closed-set classification steps.

Jev is a System One model: it answers typed questions (choice, yes/no) with calibrated
probabilities instead of generating text. Callers ask Jev first and fall back to their
OpenAI agent whenever this returns None or the answer's confidence is below
JEV_MIN_CONFIDENCE. Served through OpenRouter's System One API, which
speaks TypeSafe's protocol: https://docs.typesafe.ai/api
"""

import logging
from collections.abc import Mapping
from typing import Annotated, Any, Literal

import httpx2
import logfire
from pydantic import BaseModel, Field, ValidationError

from app.config import config

logger = logging.getLogger(__name__)

JEV_MIN_CONFIDENCE = 0.8
JEV_STATE_MAX_CHARS = 5000

_SYSTEM_ONE_PATH = "/v1/systemone"
_TIMEOUT_SECONDS = 10.0


class ChoiceAnswer(BaseModel):
    type: Literal["choice"]
    choice: str
    confidence: float
    probabilities: dict[str, float]


class NoulAnswer(BaseModel):
    type: Literal["noul"]
    noul: float = Field(description="Probability of a yes answer, from 0 to 1")


class SystemOneResponse(BaseModel):
    model: str
    answers: dict[str, Annotated[ChoiceAnswer | NoulAnswer, Field(discriminator="type")]]


def choice_question(instructions: str, criteria: Mapping[str, str | None]) -> dict[str, Any]:
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


def noul_question(instructions: str, true: str | None = None) -> dict[str, Any]:
    question: dict[str, Any] = {"type": "noul", "instructions": instructions}
    if true is not None:
        question["criteria"] = {"true": true}
    return question


_client: httpx2.AsyncClient | None = None


def _get_client() -> httpx2.AsyncClient | None:
    """Singleton HTTP client, or None when Jev is not configured."""
    global _client
    if not config.OPENROUTER_API_KEY:
        return None
    if _client is None:
        _client = httpx2.AsyncClient(
            base_url=config.JEV_BASE_URL,
            headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
            timeout=_TIMEOUT_SECONDS,
        )
    return _client


async def ask_jev(
    step: str,
    state: str | dict[str, Any],
    questions: Mapping[str, dict[str, Any]],
) -> SystemOneResponse | None:
    """Ask Jev the named questions about state; None when unconfigured or on any failure."""
    client = _get_client()
    if client is None:
        return None
    body = {"state": state, "model": config.JEV_MODEL, "questions": dict(questions)}
    with logfire.span("jev", step=step):
        try:
            try:
                response = await client.post(_SYSTEM_ONE_PATH, json=body)
            except httpx2.TimeoutException:
                response = await client.post(_SYSTEM_ONE_PATH, json=body)
            response.raise_for_status()
            return SystemOneResponse.model_validate_json(response.content)
        except httpx2.HTTPStatusError as e:
            logger.warning("Jev %s request failed, falling back to OpenAI: %s %s", step, e, e.response.text[:500])
            return None
        except (httpx2.HTTPError, ValidationError) as e:
            logger.warning("Jev %s request failed, falling back to OpenAI: %s", step, e)
            return None


def confident_choice(response: SystemOneResponse, name: str) -> ChoiceAnswer | None:
    answer = response.answers.get(name)
    if isinstance(answer, ChoiceAnswer) and answer.confidence >= JEV_MIN_CONFIDENCE:
        return answer
    return None


def confidence_level(probability: float) -> Literal["low", "medium", "high"]:
    if probability >= 0.9:
        return "high"
    if probability >= 0.7:
        return "medium"
    return "low"
