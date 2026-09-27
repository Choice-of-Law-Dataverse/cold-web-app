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
from app.case_analyzer.tools.jurisdiction_detector import (
    detect_legal_system_by_jurisdiction,
    detect_legal_system_type,
    legal_system_from_family,
)
from app.case_analyzer.tools.models import StepResult, Theme, ThemeClassificationOutput
from app.case_analyzer.tools.theme_classifier import classify_themes, jev_theme_probabilities
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
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "test-key")

    def install(handler: Callable[[httpx2.Request], httpx2.Response]) -> None:
        client = httpx2.AsyncClient(base_url="https://jev.test", transport=httpx2.MockTransport(handler))
        monkeypatch.setattr(jev, "_client", client)

    return install


@pytest.mark.asyncio
async def test_ask_jev_is_disabled_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", None)
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
    assert body["model"] == config.JEV_MODEL
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
async def test_jurisdiction_uses_csv_code_and_mapped_legal_system(use_jev) -> None:
    requests: list[dict[str, Any]] = []
    use_jev(_respond({"jurisdiction": _choice("Switzerland", 0.97)}, requests))

    with (
        patch("app.case_analyzer.tools.jurisdiction_classifier.Runner.run", new=AsyncMock()) as runner,
        patch("app.case_analyzer.tools.jurisdiction_detector.Runner.run", new=AsyncMock()) as legal_system_runner,
    ):
        result = await detect_precise_jurisdiction_with_confidence(DECISION_TEXT)

    runner.assert_not_awaited()
    legal_system_runner.assert_not_awaited()
    assert [set(body["questions"]) for body in requests] == [{"jurisdiction"}]
    assert result.precise_jurisdiction == "Switzerland"
    assert result.jurisdiction_code == "CHE"
    assert result.legal_system_type == "Civil-law jurisdiction"
    assert result.confidence == "high"
    assert jev.answered_by_jev(result.reasoning)


@pytest.mark.asyncio
async def test_jurisdiction_asks_legal_system_for_unmapped_jurisdiction(use_jev) -> None:
    requests: list[dict[str, Any]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        questions = json.loads(request.content)["questions"]
        answer = _choice("Aruba", 0.95) if "jurisdiction" in questions else _choice("Civil-law jurisdiction", 0.9)
        return _respond({next(iter(questions)): answer}, requests)(request)

    use_jev(handler)
    result = await detect_precise_jurisdiction_with_confidence(DECISION_TEXT)

    assert [set(body["questions"]) for body in requests] == [{"jurisdiction"}, {"legal_system"}]
    assert requests[1]["state"]["jurisdiction"] == "Aruba"
    assert result.jurisdiction_code == "ABW"
    assert result.legal_system_type == "Civil-law jurisdiction"


@pytest.mark.asyncio
async def test_jurisdiction_keeps_result_when_legal_system_detection_fails(use_jev) -> None:
    use_jev(_respond({"jurisdiction": _choice("Aruba", 0.95)}))

    with (
        patch("app.case_analyzer.tools.jurisdiction_detector.get_openai_client"),
        patch("app.case_analyzer.tools.jurisdiction_detector.Runner.run", new=AsyncMock(side_effect=RuntimeError)),
    ):
        result = await detect_precise_jurisdiction_with_confidence(DECISION_TEXT)

    assert result.jurisdiction_code == "ABW"
    assert result.legal_system_type == "Unknown"


def test_usage_becomes_genai_span_attributes() -> None:
    response = jev.SystemOneResponse.model_validate(
        {"model": "jev-1", "answers": {}, "usage": {"input_tokens": 275, "output_tokens": 20, "cost": 0.00003}}
    )
    attributes = jev._usage_attributes(response)
    assert attributes["gen_ai.request.model"] == config.JEV_MODEL
    assert attributes["gen_ai.usage.input_tokens"] == 275
    assert attributes["operation.cost"] == 0.00003
    assert "operation.cost" not in jev._usage_attributes(jev.SystemOneResponse(model="jev-1", answers={}))


def _theme_answers(probabilities: dict[str, float]) -> dict[str, Any]:
    return {theme: {"type": "noul", "noul": probabilities.get(theme, 0.02)} for theme in get_args(Theme)}


@pytest.mark.asyncio
async def test_themes_selects_decisive_jev_answers(use_jev) -> None:
    use_jev(_respond(_theme_answers({"Tacit choice": 0.91})))

    with patch("app.case_analyzer.tools.theme_classifier.run_agent", new=AsyncMock()) as agent:
        step = await classify_themes(
            DocumentContext(draft_id=1, text=DECISION_TEXT), "Art. 116 PILA", "Civil-law jurisdiction", "Switzerland"
        )

    agent.assert_not_awaited()
    assert step.output.themes == ["Party autonomy", "Tacit choice"]
    assert jev.answered_by_jev(step.output.reasoning)
    assert step.evidence["jev_probabilities"]["Party autonomy"] == 0.91


@pytest.mark.asyncio
async def test_theme_probabilities_follow_the_hierarchy(use_jev) -> None:
    requests: list[dict[str, Any]] = []
    use_jev(_respond(_theme_answers({"Dépeçage": 0.9, "Freedom of Choice": 0.4}), requests))

    result = await jev_theme_probabilities("The parties chose different laws for the guarantee and the loan.")

    assert result is not None
    _model, probabilities = result
    assert "Party autonomy" not in requests[0]["questions"]
    assert probabilities["Freedom of Choice"] == 0.9
    assert probabilities["Party autonomy"] == 0.9
    question = requests[0]["questions"]["Tacit choice"]
    assert question["instructions"]["theme"]["name"] == "Tacit choice"
    assert set(question["criteria"]) == {"true", "false"}


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


@pytest.mark.asyncio
async def test_ask_jev_retries_once_on_timeout(use_jev) -> None:
    calls: list[int] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(1)
        if len(calls) == 1:
            raise httpx2.ReadTimeout("slow", request=request)
        return _respond({"q": {"type": "noul", "noul": 0.9}})(request)

    use_jev(handler)
    response = await jev.ask_jev("step", "text", {"q": jev.noul_question("?")})

    assert response is not None
    assert len(calls) == 2


@pytest.mark.parametrize(
    ("family", "expected"),
    [
        ("Civil Law", "Civil-law jurisdiction"),
        ("Hybrid,Religious Law,Civil Law", "Civil-law jurisdiction"),
        ("Hybrid,Common Law", "Common-law jurisdiction"),
        ("Roman-Dutch Law", None),
        ("Hybrid,Common Law,Civil Law", None),
        ("Supranational Law", None),
        ("", None),
    ],
)
def test_legal_system_from_curated_family(family: str, expected: str | None) -> None:
    assert legal_system_from_family(family) == expected


def test_curated_family_decides_known_jurisdictions() -> None:
    assert detect_legal_system_by_jurisdiction("Quebec (Canada)") == "Civil-law jurisdiction"
    assert detect_legal_system_by_jurisdiction("Canada") == "Common-law jurisdiction"
    assert detect_legal_system_by_jurisdiction("South Africa") is None


@pytest.mark.asyncio
async def test_ask_jev_returns_none_on_unexpected_errors(use_jev) -> None:
    def handler(_request: httpx2.Request) -> httpx2.Response:
        raise RuntimeError("client closed")

    use_jev(handler)
    assert await jev.ask_jev("step", "text", {"q": jev.noul_question("?")}) is None


@pytest.mark.asyncio
async def test_legal_system_uses_the_jurisdiction_step_answer_before_the_llm(use_jev) -> None:
    use_jev(_respond({"legal_system": _choice("Civil-law jurisdiction", 0.5)}))

    with patch("app.case_analyzer.tools.jurisdiction_detector.Runner.run", new=AsyncMock()) as runner:
        result = await detect_legal_system_type("Atlantis", DECISION_TEXT, fallback="Common-law jurisdiction")

    assert result == "Common-law jurisdiction"
    runner.assert_not_awaited()
