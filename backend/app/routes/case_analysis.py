import base64
import logging

import logfire
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth import require_user, verify_frontend_request
from app.case_analysis.models import JurisdictionOutput
from app.case_analysis.utils.pdf_handler import extract_text_from_pdf
from app.schemas.case_analysis import (
    ConfirmAnalysisRequest,
    UploadDocumentRequest,
    UploadDocumentResponse,
)
from app.services.analysis_cache import analysis_cache
from app.services.case_analysis import analyze_case_streaming, detect_jurisdiction
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/case-analysis", tags=["Case Analysis"], dependencies=[Depends(verify_frontend_request)]
)


def get_suggestion_service() -> SuggestionService:
    """Dependency function to get SuggestionService instance."""
    return SuggestionService()


@router.post(
    "/upload",
    summary="Upload court decision document for initial analysis",
    description=(
        "Upload a PDF court decision document. The system will extract text, "
        "detect jurisdiction and legal system type, save as draft in database, "
        "and return a correlation ID for tracking the analysis."
    ),
    response_model=UploadDocumentResponse,
)
async def upload_document(
    body: UploadDocumentRequest,
    request: Request,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
):
    """
    Upload and process a court decision document.

    Steps:
    1. Decode base64 PDF content
    2. Extract text using pymupdf4llm
    3. Detect jurisdiction and legal system type
    4. Save draft to database with full text
    5. Cache the text with a correlation ID (for session)
    6. Return initial analysis results

    Returns:
        UploadDocumentResponse with correlation_id, extracted_text, and jurisdiction info
    """
    with logfire.span("upload_document", file_name=body.file_name):
        try:
            pdf_bytes = base64.b64decode(body.file_content_base64)
            logger.info("Decoding PDF file: %s (%d bytes)", body.file_name, len(pdf_bytes))
        except Exception as e:
            logger.error("Failed to decode base64 PDF content: %s", str(e))
            raise HTTPException(status_code=400, detail="Invalid base64-encoded PDF content") from e

        try:
            extracted_text = extract_text_from_pdf(pdf_bytes)
            logger.info("Extracted %d characters from PDF", len(extracted_text))
        except Exception as e:
            logger.error("Failed to extract text from PDF: %s", str(e))
            raise HTTPException(status_code=422, detail=f"Failed to extract text from PDF: {str(e)}") from e

        try:
            jurisdiction_result: JurisdictionOutput = detect_jurisdiction(extracted_text)
            logger.info("Detected jurisdiction: %s", jurisdiction_result.precise_jurisdiction)
        except Exception as e:
            logger.error("Failed to detect jurisdiction: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to detect jurisdiction: {str(e)}") from e

        jurisdiction_data = {
            "legal_system_type": jurisdiction_result.legal_system_type,
            "precise_jurisdiction": jurisdiction_result.precise_jurisdiction,
            "jurisdiction_code": jurisdiction_result.jurisdiction_code,
            "confidence": jurisdiction_result.confidence,
            "reasoning": jurisdiction_result.reasoning,
        }

        # Create cache entry for session
        correlation_id = analysis_cache.create_entry(extracted_text, jurisdiction_data)
        logger.info("Created cache entry with correlation_id: %s", correlation_id)

        # Persist to database as draft
        draft_payload = {
            "status": "draft",
            "file_name": body.file_name,
            "full_text": extracted_text,
            "jurisdiction": jurisdiction_data,
            "correlation_id": correlation_id,
            "analysis_results": {},
        }

        try:
            draft_id = service.save_suggestion(
                payload=draft_payload,
                table="case_analyzer",
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
                source="case_analyzer_workflow",
                user=user,
            )
            logger.info("Saved draft to database with ID: %d", draft_id)

            # Store draft_id in cache for later updates
            analysis_cache.update_results(correlation_id, "draft_id", {"draft_id": draft_id})
        except Exception as e:
            logger.error("Failed to save draft to database: %s", str(e))
            # Continue even if database save fails - we have cache

        analysis_cache.cleanup_expired()

        return UploadDocumentResponse(
            correlation_id=correlation_id,
            extracted_text=extracted_text[:500],
            jurisdiction=jurisdiction_result,
        )


@router.post(
    "/analyze",
    summary="Confirm jurisdiction and run full case analysis",
    description=(
        "Confirm or correct the detected jurisdiction and run the full case analysis workflow. "
        "Returns a stream of intermediate results as each analysis step completes. "
        "Updates the database draft at each step for recoverability."
    ),
)
async def analyze_document(
    body: ConfirmAnalysisRequest,
    service: SuggestionService = Depends(get_suggestion_service),
):
    """
    Execute full case analysis workflow with streaming results.

    Steps:
    1. Retrieve cached text using correlation_id
    2. Use confirmed jurisdiction info
    3. Execute analysis workflow:
       - COL section extraction
       - Theme classification
       - Case citation extraction
       - Abstract generation
       - Relevant facts extraction
       - PIL provisions extraction
       - COL issue extraction
       - Court's position extraction
    4. Stream results as Server-Sent Events
    5. Update database at each step for workflow recovery

    Returns:
        StreamingResponse with analysis steps as SSE
    """
    with logfire.span("analyze_document", correlation_id=body.correlation_id):
        cache_entry = analysis_cache.get_entry(body.correlation_id)

        if not cache_entry:
            logger.error("Invalid or expired correlation_id: %s", body.correlation_id)
            raise HTTPException(status_code=404, detail="Invalid or expired correlation_id")

        text = cache_entry["text"]
        logger.info("Retrieved cached text (%d chars) for analysis", len(text))

        # Get draft_id from cache
        draft_result = cache_entry.get("analysis_results", {}).get("draft_id", {})
        draft_id = draft_result.get("draft_id") if isinstance(draft_result, dict) else None

        jurisdiction_data = {
            "legal_system_type": body.jurisdiction.legal_system_type,
            "precise_jurisdiction": body.jurisdiction.precise_jurisdiction,
            "jurisdiction_code": body.jurisdiction.jurisdiction_code,
            "confidence": body.jurisdiction.confidence,
            "reasoning": body.jurisdiction.reasoning,
        }

        # Update jurisdiction if it was corrected
        if draft_id:
            try:
                service.update_payload(
                    "case_analyzer",
                    draft_id,
                    {"jurisdiction": jurisdiction_data, "status": "analyzing"},
                )
                logger.info("Updated jurisdiction in draft ID: %d", draft_id)
            except Exception as e:
                logger.error("Failed to update jurisdiction in database: %s", str(e))

        async def event_generator():
            """Generate SSE events for each analysis step."""
            import json

            try:
                async for result in analyze_case_streaming(text, jurisdiction_data):
                    # Update cache
                    analysis_cache.update_results(body.correlation_id, result.get("step", "unknown"), result)

                    # Update database if we have draft_id and step data
                    if draft_id and result.get("status") == "completed" and result.get("data"):
                        try:
                            step_name = result.get("step", "unknown")
                            update_data = {f"analysis_results.{step_name}": result.get("data")}
                            service.update_payload("case_analyzer", draft_id, update_data)
                            logger.info("Updated step %s in draft ID: %d", step_name, draft_id)
                        except Exception as e:
                            logger.error("Failed to update step %s in database: %s", step_name, str(e))

                    event_data = json.dumps(result)
                    yield f"data: {event_data}\n\n"

                # Mark as completed when all steps are done
                if draft_id:
                    try:
                        service.update_payload("case_analyzer", draft_id, {"status": "completed"})
                        logger.info("Marked draft ID %d as completed", draft_id)
                    except Exception as e:
                        logger.error("Failed to mark draft as completed: %s", str(e))

                yield 'data: {"done": true}\n\n'
            except Exception as e:
                logger.error("Analysis workflow failed: %s", str(e))

                # Mark as failed in database
                if draft_id:
                    try:
                        service.update_payload(
                            "case_analyzer",
                            draft_id,
                            {"status": "failed", "error": str(e)}
                        )
                    except Exception as db_error:
                        logger.error("Failed to mark draft as failed: %s", str(db_error))

                error_event = json.dumps({"step": "error", "status": "error", "error": str(e)})
                yield f"data: {error_event}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
