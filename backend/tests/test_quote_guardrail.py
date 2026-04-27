"""Tests for the supporting_quotes output guardrail."""

from typing import Any

import pytest
from agents.run_context import RunContextWrapper
from agents.usage import Usage

from app.case_analyzer.quote_guardrail import verify_supporting_quotes as _verify_guardrail
from app.case_analyzer.tools.document_nav import DocumentContext
from app.case_analyzer.tools.models import CourtsPositionOutput, ThemeClassificationOutput

_guardrail: Any = _verify_guardrail

SOURCE_TEXT = """
The court held that French law applies to the contract.
Party autonomy is a fundamental principle under Art. 3 Rome I.
The plaintiff failed to establish a valid choice of law agreement.
"""


@pytest.fixture
def doc() -> DocumentContext:
    return DocumentContext(draft_id=1, text=SOURCE_TEXT)


def _ctx(doc_ctx: DocumentContext) -> RunContextWrapper[DocumentContext]:
    return RunContextWrapper(context=doc_ctx, usage=Usage())


class TestVerifySupportingQuotes:
    @pytest.mark.asyncio
    async def test_valid_verbatim_quote_passes(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="French law applies.",
            confidence="high",
            reasoning="Clear from the decision.",
            supporting_quotes=["French law applies to the contract."],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert not result.output.tripwire_triggered
        assert result.output.output_info["missing_quotes"] == []

    @pytest.mark.asyncio
    async def test_fabricated_quote_triggers_tripwire(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="German law applies.",
            confidence="high",
            reasoning="Made up.",
            supporting_quotes=["The court applied German law to the entire dispute."],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert result.output.tripwire_triggered
        assert len(result.output.output_info["missing_quotes"]) == 1

    @pytest.mark.asyncio
    async def test_whitespace_difference_in_quote_passes(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="French law.",
            confidence="high",
            reasoning="Correct.",
            supporting_quotes=["Party  autonomy  is  a  fundamental  principle"],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert not result.output.tripwire_triggered

    @pytest.mark.asyncio
    async def test_case_difference_in_quote_passes(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="French law.",
            confidence="high",
            reasoning="Correct.",
            supporting_quotes=["PARTY AUTONOMY IS A FUNDAMENTAL PRINCIPLE UNDER ART. 3 ROME I."],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert not result.output.tripwire_triggered

    @pytest.mark.asyncio
    async def test_model_without_supporting_quotes_passes(self, doc: DocumentContext) -> None:
        output = ThemeClassificationOutput(
            themes=["Party autonomy"],
            confidence="high",
            reasoning="Theme evident from text.",
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert not result.output.tripwire_triggered

    @pytest.mark.asyncio
    async def test_empty_supporting_quotes_passes(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="French law.",
            confidence="high",
            reasoning="Correct.",
            supporting_quotes=[],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert not result.output.tripwire_triggered

    @pytest.mark.asyncio
    async def test_mixed_valid_and_fabricated_triggers_tripwire(self, doc: DocumentContext) -> None:
        output = CourtsPositionOutput(
            courts_position="French law.",
            confidence="high",
            reasoning="Mixed.",
            supporting_quotes=[
                "French law applies to the contract.",
                "The defendant was found to have breached Swiss law.",
            ],
        )
        result = await _guardrail.run(_ctx(doc), None, output)
        assert result.output.tripwire_triggered
        assert len(result.output.output_info["missing_quotes"]) == 1
