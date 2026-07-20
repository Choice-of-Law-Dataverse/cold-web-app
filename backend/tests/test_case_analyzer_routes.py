"""Focused route tests for case-analyzer authorization and upload limits."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.auth import EMAIL_CLAIM
from app.routes.case_analyzer import analyze_document, upload_document
from app.schemas.case_analyzer import ConfirmAnalysisRequest, UploadDocumentRequest


def _decode_stream_chunk(chunk: str | bytes | memoryview) -> str:
    if isinstance(chunk, str):
        return chunk
    if isinstance(chunk, memoryview):
        return chunk.tobytes().decode()
    return chunk.decode()


@pytest.mark.asyncio
async def test_analyze_rejects_draft_owned_by_another_user() -> None:
    service = MagicMock()
    service.get_case_analyzer_full.return_value = {
        "id": 7,
        "user_email": "owner@example.com",
        "data": {"pdf_url": "https://storage.example/decision.pdf"},
    }

    with pytest.raises(HTTPException) as exc_info:
        await analyze_document(
            ConfirmAnalysisRequest(draft_id=7, jurisdiction=None, jurisdiction_confirmed=False, resume=False),
            user={EMAIL_CLAIM: "attacker@example.com"},
            service=service,
        )

    assert exc_info.value.status_code == 403
    service.update_moderation_status.assert_not_called()
    service.clear_analyzer_steps.assert_not_called()


@pytest.mark.asyncio
async def test_analyze_requires_identifiable_user() -> None:
    service = MagicMock()
    service.get_case_analyzer_full.return_value = {"id": 7, "user_email": "owner@example.com"}

    with pytest.raises(HTTPException) as exc_info:
        await analyze_document(
            ConfirmAnalysisRequest(draft_id=7, jurisdiction=None, jurisdiction_confirmed=False, resume=False),
            user={},
            service=service,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_analyze_fails_closed_when_draft_has_no_owner() -> None:
    service = MagicMock()
    service.get_case_analyzer_full.return_value = {"id": 7, "user_email": None}

    with pytest.raises(HTTPException) as exc_info:
        await analyze_document(
            ConfirmAnalysisRequest(draft_id=7, jurisdiction=None, jurisdiction_confirmed=False, resume=False),
            user={EMAIL_CLAIM: "owner@example.com"},
            service=service,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_blob_url_upload_rejects_oversized_download_before_extraction() -> None:
    oversized_pdf = b"x" * 11
    body = UploadDocumentRequest(file_name="large.pdf", blob_url="https://storage.example/large.pdf")
    request = MagicMock()
    service = MagicMock()

    with (
        patch(
            "app.routes.case_analyzer.download_blob_with_managed_identity",
            return_value=oversized_pdf,
        ),
        patch("app.routes.case_analyzer.MAX_PDF_SIZE_BYTES", 10),
        patch("app.routes.case_analyzer.extract_text_from_pdf") as extract_text,
    ):
        response = await upload_document(body, request, user={EMAIL_CLAIM: "owner@example.com"}, service=service)
        body_chunks = [chunk async for chunk in response.body_iterator]

    response_text = "".join(_decode_stream_chunk(chunk) for chunk in body_chunks)
    assert "PDF file too large" in response_text
    extract_text.assert_not_called()
    service.save_suggestion.assert_not_called()
