"""Tests for the Jev-first classification steps and their OpenAI fallback."""

import json
from collections.abc import Callable
from typing import Any, get_args
from unittest.mock import AsyncMock, MagicMock, patch

import httpx2
import pytest

from app.case_analyzer import jev
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.jurisdiction_classifier import detect_precise_jurisdiction_with_confidence
from app.case_analyzer.tools.jurisdiction_detector import detect_legal_system_type
from app.case_analyzer.tools.models import StepResult, Theme, ThemeClassificationOutput
from app.case_analyzer.tools.theme_classifier import classify_themes
from app.config import config

DECISION_TEXT = "The Federal Supreme Court held that the parties validly chose Swiss law. " * 3


def _choice(choice: str, confidence: float) -> dict[str, Any]:
    return {"type": "choice", "choice": choice, "confidence": confidence, "probabilities": {choice: confidence}}


def _respond(
    answers: dict[str, Any], requests: list[dict[str, Any]] | None = None
) -> Callable[[httpx2.Request], httpx2.Response]:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if requests is not None:
            requests.append(json.loads(request.content))
        return httpx2.Response(200, json={"model": "jev-1", "answers": answers, "usage": {}})

    return handler


@pytest.fixture
def use_jev(monkeypatch: pytest.MonkeyPatch) -> Callable[[Callable[[httpx2.Request], httpx2.Response]], None]:
    monkeypatch.setattr(config, "TYPESAFE_API_KEY", "test-key")

    def install(handler: Callable[[httpx2.Request], httpx2.Response]) -> None:
        client = httpx2.AsyncClient(base_url="https://jev.test", transport=httpx2.MockTransport(handler))
        monkeypatch.setattr(jev, "_client", client)

    return install


@pytest.mark.asyncio
async def test_ask_jev_is_disabled_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "TYPESAFE_API_KEY", None)
    assert await jev.ask_jev("step", "text", {"q": jev.noul_question("?")}) is None


@pytest.mark.asyncio
async def test_ask_jev_returns_none_on_http_error(use_jev) -> None:
    use_jev(lambda _request: httpx2.Response(500, json={"detail": "boom"}))
    assert await jev.ask_jev("step", "text", {"q": jev.noul_question("?")}) is None


@pytest.mark.asyncio
async def test_legal_system_uses_confident_jev_answer(use_jev) -> None:
    requests: list[dict[str, Any]] = []
    use_jev(_respond({"legal_system": _choice("Common-law jurisdiction", 0.95)}, requests))

    with patch("app.case_analyzer.tools.jurisdiction_detector.Runner.run", new=AsyncMock()) as runner:
        result = await detect_legal_system_type("Atlantis", DECISION_TEXT)

    assert result == "Common-law jurisdiction"
    runner.assert_not_awaited()
    body = requests[0]
    assert body["model"] == config.TYPESAFE_MODEL
    assert body["state"]["jurisdiction"] == "Atlantis"
    assert set(body["questions"]["legal_system"]["criteria"]) == {
        "Civil-law jurisdiction",
        "Common-law jurisdiction",
        "No court decision",
    }


@pytest.mark.asyncio
async def test_legal_system_falls_back_when_jev_is_unsure(use_jev) -> None:
    use_jev(_respond({"legal_system": _choice("Common-law jurisdiction", 0.55)}))
    fallback = MagicMock(final_output="Civil-law jurisdiction")

    with (
        patch("app.case_analyzer.tools.jurisdiction_detector.get_openai_client"),
        patch("app.case_analyzer.tools.jurisdiction_detector.Runner.run", new=AsyncMock(return_value=fallback)) as runner,
    ):
        result = await detect_legal_system_type("Atlantis", DECISION_TEXT)

    assert result == "Civil-law jurisdiction"
    runner.assert_awaited_once()


@pytest.mark.asyncio
async def test_jurisdiction_uses_csv_code_for_jev_answer(use_jev) -> None:
    use_jev(
        _respond(
            {
                "jurisdiction": _choice("Switzerland", 0.97),
                "legal_system": _choice("Civil-law jurisdiction", 0.92),
            }
        )
    )

    with patch("app.case_analyzer.tools.jurisdiction_classifier.Runner.run", new=AsyncMock()) as runner:
        result = await detect_precise_jurisdiction_with_confidence(DECISION_TEXT)

    runner.assert_not_awaited()
    assert result.precise_jurisdiction == "Switzerland"
    assert result.jurisdiction_code == "CHE"
    assert result.legal_system_type == "Civil-law jurisdiction"
    assert result.confidence == "high"


def _theme_answers(probabilities: dict[str, float]) -> dict[str, Any]:
    return {theme: {"type": "noul", "noul": probabilities.get(theme, 0.02)} for theme in get_args(Theme)}


@pytest.mark.asyncio
async def test_themes_selects_decisive_jev_answers(use_jev) -> None:
    use_jev(_respond(_theme_answers({"Party autonomy": 0.97, "Tacit choice": 0.91})))

    with patch("app.case_analyzer.tools.theme_classifier.run_agent", new=AsyncMock()) as agent:
        step = await classify_themes(
            DocumentContext(draft_id=1, text=DECISION_TEXT), "Art. 116 PILA", "Civil-law jurisdiction", "Switzerland"
        )

    agent.assert_not_awaited()
    assert step.output.themes == ["Party autonomy", "Tacit choice"]
    assert step.evidence["jev_probabilities"]["Party autonomy"] == 0.97


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "probabilities",
    [
        pytest.param({"Party autonomy": 0.97, "Public policy": 0.6}, id="undecided theme"),
        pytest.param({}, id="no theme applies"),
    ],
)
@pytest.mark.asyncio
async def test_themes_fall_back_to_agent(use_jev, probabilities: dict[str, float]) -> None:
    use_jev(_respond(_theme_answers(probabilities)))
    fallback = StepResult(output=ThemeClassificationOutput(themes=["NA"], confidence="high", reasoning="ok"))

    with (
        patch("app.case_analyzer.tools.theme_classifier.get_openai_client"),
        patch("app.case_analyzer.tools.theme_classifier.run_agent", new=AsyncMock(return_value=fallback)) as agent,
    ):
        step = await classify_themes(
            DocumentContext(draft_id=1, text=DECISION_TEXT), "Art. 116 PILA", "Civil-law jurisdiction", "Switzerland"
        )

    agent.assert_awaited_once()
    assert step is fallback
