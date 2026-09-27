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
JEV_REASONING_PREFIX = "Classified by Jev"

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


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float | None = Field(default=None, description="USD, reported by OpenRouter")


class SystemOneResponse(BaseModel):
    model: str
    answers: dict[str, Annotated[ChoiceAnswer | NoulAnswer, Field(discriminator="type")]]
    usage: Usage = Usage()


def choice_question(instructions: str, criteria: Mapping[str, str | None]) -> dict[str, Any]:
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


type Entry = str | dict[str, Any] | list[Any]
"""System One accepts plain text or JSON structure for instructions and criteria."""


def noul_question(instructions: Entry, true: Entry | None = None, false: Entry | None = None) -> dict[str, Any]:
    """A yes/no question; OpenRouter rejects criteria unless both outcomes are described."""
    question: dict[str, Any] = {"type": "noul", "instructions": instructions}
    if true is not None and false is not None:
        question["criteria"] = {"true": true, "false": false}
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
    with logfire.span("jev", step=step) as span:
        try:
            try:
                response = await client.post(_SYSTEM_ONE_PATH, json=body)
            except httpx2.TimeoutException:
                response = await client.post(_SYSTEM_ONE_PATH, json=body)
            response.raise_for_status()
            result = SystemOneResponse.model_validate_json(response.content)
            span.set_attributes(_usage_attributes(result))
            return result
        except httpx2.HTTPStatusError as e:
            logger.warning("Jev %s request failed, falling back to OpenAI: %s %s", step, e, e.response.text[:4000])
            return None
        except (httpx2.HTTPError, ValidationError) as e:
            logger.warning("Jev %s request failed, falling back to OpenAI: %s", step, e)
            return None
        except Exception as e:
            logger.warning("Jev %s request raised %s, falling back to OpenAI: %s", step, type(e).__name__, e)
            return None


def _usage_attributes(response: SystemOneResponse) -> dict[str, Any]:
    """GenAI span attributes, so Logfire and pydantic-evals count Jev's tokens and cost like OpenAI's."""
    attributes: dict[str, Any] = {
        "gen_ai.request.model": config.JEV_MODEL,
        "gen_ai.response.model": response.model,
        "gen_ai.usage.input_tokens": response.usage.input_tokens,
        "gen_ai.usage.output_tokens": response.usage.output_tokens,
    }
    if response.usage.cost is not None:
        attributes["operation.cost"] = response.usage.cost
    return attributes


def jev_reasoning(model: str, detail: str) -> str:
    """Reasoning text for an answer Jev gave; answered_by_jev recognises it."""
    return f"{JEV_REASONING_PREFIX} ({model}): {detail}"


def answered_by_jev(reasoning: str) -> bool:
    return reasoning.startswith(JEV_REASONING_PREFIX)


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
