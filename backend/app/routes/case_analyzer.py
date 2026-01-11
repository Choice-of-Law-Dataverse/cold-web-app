import base64
import json
import logging
import traceback
from typing import Any

import logfire
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth import require_user, verify_frontend_request
from app.case_analyzer import (
    JurisdictionOutput,
    analyze_case_streaming,
    detect_jurisdiction,
    extract_text_from_pdf,
)
from app.schemas.case_analyzer import (
    ConfirmAnalysisRequest,
    JurisdictionInfo,
    SubmitForApprovalRequest,
    SubmitForApprovalResponse,
    UploadDocumentRequest,
    UploadDocumentResponse,
)
from app.services.azure_storage import (
    download_blob_with_managed_identity,
    get_text_from_blob,
    upload_blob_with_managed_identity,
)
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/case-analyzer", tags=["Case Analyzer"], dependencies=[Depends(verify_frontend_request)])

MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024


def get_suggestion_service() -> SuggestionService:
    """Dependency function to get SuggestionService instance."""
    return SuggestionService()


@router.post(
    "/upload",
    summary="Upload court decision document for initial analysis",
    description=(
        "Upload a PDF court decision document. The system will extract text, "
        "detect jurisdiction and legal system type, save as draft in database, "
        "and return a draft ID for tracking the analysis."
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
    4. Save draft to database with full text and PDF URL
    5. Return draft_id, extracted_text, and jurisdiction info

    Returns:
        UploadDocumentResponse with draft_id, extracted_text, and jurisdiction info
    """
    with logfire.span("upload_document", file_name=body.file_name, blob_url=body.blob_url[:100]):
        azure_blob_url: str

        try:
            if body.blob_url.startswith("data:application/pdf;base64,"):
                base64_content = body.blob_url.replace("data:application/pdf;base64,", "")
                pdf_bytes = base64.b64decode(base64_content)

                if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"PDF file too large ({len(pdf_bytes) / 1024 / 1024:.1f}MB). Maximum size is {MAX_PDF_SIZE_BYTES / 1024 / 1024}MB",
                    )

                try:
                    azure_blob_url = upload_blob_with_managed_identity(pdf_bytes, body.file_name)
                except Exception as upload_error:
                    logger.error("Failed to upload PDF to Azure: %s", str(upload_error))
                    raise HTTPException(
                        status_code=500, detail="Failed to upload PDF to storage. Please try again or contact support."
                    ) from upload_error
            else:
                pdf_bytes = download_blob_with_managed_identity(body.blob_url)
                azure_blob_url = body.blob_url
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get PDF content: %s", str(e))
            raise HTTPException(status_code=400, detail="Failed to get PDF content") from e

        try:
            extracted_text = extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            logger.error("Failed to extract text from PDF: %s", str(e))
            raise HTTPException(status_code=422, detail=f"Failed to extract text from PDF: {str(e)}") from e

        try:
            jurisdiction_result: JurisdictionOutput = await detect_jurisdiction(extracted_text)
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

        draft_payload = {
            "file_name": body.file_name,
            "pdf_url": azure_blob_url,
            "full_text": extracted_text,
            "moderation_status": "draft",
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

            # Store jurisdiction_data directly - it already contains all fields
            # (legal_system_type, precise_jurisdiction, jurisdiction_code, confidence, reasoning)
            service.update_analyzer_step(draft_id, "jurisdiction", jurisdiction_data)
        except Exception as e:
            logger.error("Failed to save draft to database: %s", str(e))
            raise HTTPException(status_code=500, detail="Failed to save draft to database") from e

        return UploadDocumentResponse(
            draft_id=draft_id,
            extracted_text=extracted_text,
            jurisdiction=JurisdictionInfo(
                legal_system_type=jurisdiction_result.legal_system_type,
                precise_jurisdiction=jurisdiction_result.precise_jurisdiction,
                jurisdiction_code=jurisdiction_result.jurisdiction_code,
                confidence=jurisdiction_result.confidence,
                reasoning=jurisdiction_result.reasoning,
            ),
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
    _: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
):
    """
    Execute full case analysis workflow with streaming results.

    Steps:
    1. Retrieve text from database (or Azure blob if not in DB)
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
    draft_id = body.draft_id

    with logfire.span("analyze_document", draft_id=draft_id):
        # Get the draft record to retrieve full_text and pdf_url
        record = service.get_case_analyzer_full(draft_id)
        if not record:
            logger.error("Draft not found: %d", draft_id)
            raise HTTPException(status_code=404, detail="Draft not found")

        # Get full text from database, or fetch from Azure blob if not present
        legacy_data = record.get("data", {})
        text = legacy_data.get("full_text")

        if not text:
            pdf_url = legacy_data.get("pdf_url")
            if not pdf_url:
                logger.error("No full_text or pdf_url found for draft: %d", draft_id)
                raise HTTPException(status_code=400, detail="No document text available for analysis")
            try:
                text = get_text_from_blob(pdf_url)
            except Exception as e:
                logger.error("Failed to extract text from PDF blob: %s", str(e))
                raise HTTPException(status_code=500, detail="Failed to retrieve document text") from e

        jurisdiction_data = {
            "legal_system_type": body.jurisdiction.legal_system_type,
            "precise_jurisdiction": body.jurisdiction.precise_jurisdiction,
            "jurisdiction_code": body.jurisdiction.jurisdiction_code,
            "confidence": body.jurisdiction.confidence,
            "reasoning": body.jurisdiction.reasoning,
        }

        try:
            service.update_moderation_status(draft_id, "analyzing")

            # Store jurisdiction_data directly with user_confirmed flag
            # The data already contains confidence/reasoning fields
            service.update_analyzer_step(
                draft_id,
                "jurisdiction",
                {
                    **jurisdiction_data,
                    "user_confirmed": True,
                },
            )
        except Exception as e:
            logger.error("Failed to update jurisdiction in database: %s", str(e))

        cached_results: dict[str, Any] | None = None
        if body.resume:
            try:
                analyzer_data = service.get_analyzer_data(draft_id)
                if analyzer_data:
                    cached_results = {}
                    for step_key in [
                        "col_extraction",
                        "theme_classification",
                        "case_citation",
                        "relevant_facts",
                        "pil_provisions",
                        "col_issue",
                        "courts_position",
                        "obiter_dicta",
                        "dissenting_opinions",
                        "abstract",
                    ]:
                        if step_key in analyzer_data and analyzer_data[step_key]:
                            step_result = analyzer_data[step_key]
                            if isinstance(step_result, dict) and "result" in step_result:
                                cached_results[step_key] = step_result["result"]
                            else:
                                cached_results[step_key] = step_result
            except Exception as e:
                logger.error("Failed to fetch cached results for resume: %s", str(e))

        async def event_generator():
            """Generate SSE events for each analysis step."""
            step_name: str | None = None
            with logfire.span(
                "case_analysis_stream",
                resume=body.resume,
                draft_id=draft_id,
            ):
                try:
                    async for result in analyze_case_streaming(text, jurisdiction_data, cached_results):
                        step_name = result.get("step")

                        if result.get("status") == "completed" and result.get("data"):
                            if not step_name:
                                continue
                            try:
                                step_payload = result.get("data")
                                if step_payload and isinstance(step_payload, dict):
                                    with logfire.span("persist_case_analyzer_step", step=step_name, draft_id=draft_id):
                                        # Store step_payload directly - it already contains the result data
                                        # with confidence/reasoning inside if applicable
                                        service.update_analyzer_step(draft_id, step_name, step_payload)
                            except Exception as e:
                                logger.error("Failed to update step %s in database: %s", step_name, str(e))

                        event_data = json.dumps(result)
                        yield f"data: {event_data}\n\n"

                    try:
                        with logfire.span("finalize_case_analyzer_draft", draft_id=draft_id):
                            service.update_moderation_status(draft_id, "completed")
                    except Exception as e:
                        logger.error("Failed to mark draft as completed: %s", str(e))

                    done_payload = {
                        "step": "analysis_complete",
                        "status": "completed",
                        "data": {"done": True},
                    }
                    yield f"data: {json.dumps(done_payload)}\n\n"
                except Exception as e:
                    logger.error("Analysis workflow failed: %s", str(e))
                    logger.error("Traceback: %s", traceback.format_exc())

                    try:
                        with logfire.span("fail_case_analyzer_draft", draft_id=draft_id):
                            service.update_moderation_status(draft_id, "failed")
                            service.update_analyzer_step(
                                draft_id,
                                "error",
                                {"message": str(e), "step": step_name if step_name else "unknown"},
                            )
                    except Exception as db_error:
                        logger.error("Failed to mark draft as failed: %s", str(db_error))

                    error_event = json.dumps({"step": "error", "status": "error", "error": str(e)})
                    yield f"data: {error_event}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post(
    "/submit",
    summary="Submit case analysis for moderation approval",
    description=(
        "Submit user-edited case analysis data for moderation approval. "
        "The data is stored in the submitted_data column and the status "
        "is changed to 'pending'. Moderators will review and can approve/reject."
    ),
    response_model=SubmitForApprovalResponse,
)
async def submit_for_approval(
    body: SubmitForApprovalRequest,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
):
    """
    Submit user-edited case analysis data for moderation approval.

    This endpoint:
    1. Validates the draft exists and belongs to the user
    2. Stores the user-edited data in the submitted_data column
    3. Updates moderation_status to 'pending'
    4. Returns confirmation

    The original analyzer data is preserved for audit purposes.
    """
    with logfire.span("submit_for_approval", draft_id=body.draft_id):
        # Get the full record to verify it exists
        record = service.get_case_analyzer_full(body.draft_id)

        if not record:
            logger.error("Draft not found: %d", body.draft_id)
            raise HTTPException(status_code=404, detail="Draft not found")

        # Check that the draft is in a submittable state
        current_status = record.get("moderation_status")
        if current_status in {"pending", "approved", "rejected"}:
            logger.warning(
                "Draft %d already submitted (status: %s)",
                body.draft_id,
                current_status,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Draft already submitted for moderation (status: {current_status})",
            )

        # Verify ownership - the user submitting should be the one who created the draft
        token_sub = service._get_token_sub(user)
        record_email = record.get("user_email")
        if token_sub and record_email and token_sub != record_email:
            logger.warning(
                "User %s attempted to submit draft %d owned by %s",
                token_sub,
                body.draft_id,
                record_email,
            )
            raise HTTPException(status_code=403, detail="You can only submit your own drafts")

        try:
            service.set_submitted_data(body.draft_id, body.submitted_data)

            return SubmitForApprovalResponse(
                draft_id=body.draft_id,
                status="pending",
                message="Successfully submitted for moderation approval",
            )
        except Exception as e:
            logger.error("Failed to submit draft %d: %s", body.draft_id, str(e))
            raise HTTPException(status_code=500, detail="Failed to submit for approval") from e


@router.get(
    "/draft/{draft_id}",
    summary="Get draft data for recovery",
    description=(
        "Fetch draft data to recover the analyzer form state. "
        "Returns draft data if status is recoverable (not pending/approved)."
    ),
)
async def get_draft_for_recovery(
    draft_id: int,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
) -> dict[str, Any]:
    """
    Get draft data to recover form state.

    Only returns data if:
    - Draft exists
    - User owns the draft
    - Status is recoverable (draft, analyzing, completed, failed)

    Does not return data if status is pending, approved, or rejected.
    """
    record = service.get_case_analyzer_full(draft_id)
    if not record:
        raise HTTPException(status_code=404, detail="Draft not found")

    # Verify ownership
    token_sub = service._get_token_sub(user)
    record_email = record.get("user_email")
    if token_sub and record_email and token_sub != record_email:
        raise HTTPException(status_code=403, detail="You can only access your own drafts")

    # Check status - don't allow recovery of already-submitted drafts
    status = record.get("moderation_status")
    if status in {"pending", "approved", "rejected"}:
        raise HTTPException(
            status_code=400,
            detail=f"Draft already submitted (status: {status}). Cannot recover.",
        )

    # Parse data columns
    def _parse_json(val: Any) -> dict[str, Any] | None:
        if val is None:
            return None
        if isinstance(val, dict):
            return dict(val)
        try:
            return json.loads(val)
        except Exception:
            return None

    legacy_data = _parse_json(record.get("data")) or {}
    analyzer_data = _parse_json(record.get("analyzer")) or {}

    # Extract jurisdiction info from legacy data
    jurisdiction_info = None
    if legacy_data.get("jurisdiction"):
        jurisdiction_info = legacy_data["jurisdiction"]
    elif legacy_data.get("precise_jurisdiction"):
        jurisdiction_info = {
            "precise_jurisdiction": legacy_data.get("precise_jurisdiction"),
            "jurisdiction_code": legacy_data.get("jurisdiction_code"),
            "legal_system_type": legacy_data.get("legal_system_type"),
            "confidence": legacy_data.get("jurisdiction_confidence"),
            "reasoning": legacy_data.get("jurisdiction_reasoning"),
        }

    # Get file info
    file_name = legacy_data.get("file_name")
    pdf_url = legacy_data.get("pdf_url")

    # Format created_at safely
    created_at = record.get("created_at")
    created_at_str = None
    if created_at and hasattr(created_at, "isoformat"):
        created_at_str = created_at.isoformat()

    return {
        "draft_id": draft_id,
        "status": status or "draft",
        "file_name": file_name,
        "pdf_url": pdf_url,
        "jurisdiction_info": jurisdiction_info,
        "analyzer_data": analyzer_data,
        "case_citation": record.get("case_citation"),
        "created_at": created_at_str,
    }
