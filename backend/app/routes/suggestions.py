from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.auth import require_editor_or_admin, require_user, verify_frontend_request
from app.routes.moderation import (
    MainDBWriter,
    _approve_case_analyzer,
    _get_target_table,
    _link_jurisdictions_for_default_categories,
    _normalize_domestic_instruments,
)
from app.schemas.suggestions import (
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
    RegionalInstrumentSuggestion,
    SuggestionPayload,
    SuggestionResponse,
)
from app.services.suggestions import SuggestionService

router = APIRouter(
    prefix="/suggestions",
    tags=["Suggestions"],
    dependencies=[Depends(verify_frontend_request)],
)


def get_suggestion_service() -> SuggestionService:
    """Dependency function to lazily instantiate the SuggestionService."""
    return SuggestionService()


@router.post(
    "/",
    summary="Submit a new data suggestion",
    description=("Accepts arbitrary dictionaries from the frontend and stores them in a separate Postgres table."),
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_suggestion(
    body: SuggestionPayload,
    request: Request,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {
            **body.data,
            **({"submitter_email": body.submitter_email} if body.submitter_email else {}),
            **({"submitter_comments": body.submitter_comments} if body.submitter_comments else {}),
        }
        new_id = service.save_suggestion(
            payload=payload,
            table="generic",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=body.source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/court-decisions",
    summary="Submit a new Court Decision suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_court_decision(
    body: CourtDecisionSuggestion,
    request: Request,
    user: dict = Depends(require_user),
    source: str | None = Header(None),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {"category": "court_decision", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="court_decisions",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/domestic-instruments",
    summary="Submit a new Domestic Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_domestic_instrument(
    body: DomesticInstrumentSuggestion,
    request: Request,
    user: dict = Depends(require_user),
    source: str | None = Header(None),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {"category": "domestic_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="domestic_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/regional-instruments",
    summary="Submit a new Regional Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_regional_instrument(
    body: RegionalInstrumentSuggestion,
    request: Request,
    user: dict = Depends(require_user),
    source: str | None = Header(None),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {"category": "regional_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="regional_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/international-instruments",
    summary="Submit a new International Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_international_instrument(
    body: InternationalInstrumentSuggestion,
    request: Request,
    user: dict = Depends(require_user),
    source: str | None = Header(None),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {"category": "international_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="international_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/literature",
    summary="Submit a new Literature suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_literature(
    body: LiteratureSuggestion,
    request: Request,
    user: dict = Depends(require_user),
    source: str | None = Header(None),
    service: SuggestionService = Depends(get_suggestion_service),
):
    try:
        payload = {"category": "literature", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="literature",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            user=user,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Moderation endpoints


def _table_key(path_segment: str) -> str | None:
    """Map category path segment to internal table name."""
    mapping = {
        "court-decisions": "court_decisions",
        "domestic-instruments": "domestic_instruments",
        "regional-instruments": "regional_instruments",
        "international-instruments": "international_instruments",
        "literature": "literature",
        "case-analyzer": "case_analyzer",
    }
    return mapping.get(path_segment)


@router.get(
    "/moderation/pending/{category}",
    summary="List pending suggestions for a category",
    description="Requires editor or admin role. Returns list of pending suggestions for moderation.",
)
async def list_pending_suggestions(
    category: str,
    _: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> list[dict[str, Any]]:
    """List all pending suggestions for a specific category."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        items = service.list_pending(table)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending suggestions: {str(e)}",
        ) from e


@router.get(
    "/moderation/{category}/{suggestion_id}",
    summary="Get specific suggestion details",
    description="Requires editor or admin role. Returns detailed information about a specific suggestion.",
)
async def get_suggestion_detail(
    category: str,
    suggestion_id: int,
    _: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> dict[str, Any]:
    """Get detailed information about a specific suggestion."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        item = service.get_pending_by_id(table, suggestion_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or not pending",
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestion: {str(e)}",
        ) from e


@router.post(
    "/moderation/{category}/{suggestion_id}/approve",
    summary="Approve a suggestion",
    description="Requires editor or admin role. Marks a suggestion as approved and processes it for insertion",
)
async def approve_suggestion(
    category: str,
    suggestion_id: int,
    request: Request,
    user: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> dict[str, str]:
    """Approve a suggestion and process it for persistent storage."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        item = service.get_pending_by_id(table, suggestion_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or not pending",
            )

        original_payload: dict[str, Any] = item.get("payload", {}) or {}

        # Get user email from Auth0 token
        moderator_email = user.get("https://cold.global/email") or user.get("email") or user.get("sub", "unknown")

        if category == "case-analyzer":
            # Use existing case analyzer approval logic
            await _approve_case_analyzer(request, table, suggestion_id, original_payload, item)
        else:
            # Handle default categories - simplified without form editing
            writer = MainDBWriter()
            target_table = _get_target_table(category)
            if not target_table:
                raise HTTPException(status_code=400, detail="Unsupported category")

            if target_table == "Domestic_Instruments":
                _normalize_domestic_instruments(original_payload)

            # Filter out reserved metadata fields
            _reserved = {
                "submitter_email",
                "submitter_comments",
                "official_source_pdf",
                "source_pdf",
                "attachment",
                "category",
            }
            payload_for_writer = {k: v for k, v in original_payload.items() if k not in _reserved}

            merged_id = writer.insert_record(target_table, payload_for_writer)
            _link_jurisdictions_for_default_categories(writer, target_table, merged_id, payload_for_writer)

            service.mark_status(
                table,
                suggestion_id,
                "approved",
                moderator_email,
                note="",
                merged_id=merged_id,
            )

        return {"status": "success", "message": "Suggestion approved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve suggestion: {str(e)}",
        ) from e


@router.post(
    "/moderation/{category}/{suggestion_id}/reject",
    summary="Reject a suggestion",
    description="Requires editor or admin role. Marks a suggestion as rejected.",
)
async def reject_suggestion(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> dict[str, str]:
    """Reject a suggestion."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        # Get user email from Auth0 token
        moderator_email = user.get("https://cold.global/email") or user.get("email") or user.get("sub", "unknown")

        service.mark_status(
            table,
            suggestion_id,
            "rejected",
            moderator_email,
            note="",
        )

        return {"status": "success", "message": "Suggestion rejected successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject suggestion: {str(e)}",
        ) from e
