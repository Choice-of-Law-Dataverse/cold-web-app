from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.auth import require_editor_or_admin, require_user, verify_frontend_request
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

service = SuggestionService()


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
    "/pending/{category}",
    summary="List pending suggestions for a category",
    description="Requires editor or admin role. Returns list of pending suggestions for moderation.",
)
async def list_pending_suggestions(
    category: str,
    user: dict = Depends(require_editor_or_admin),
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
    "/{category}/{suggestion_id}",
    summary="Get specific suggestion details",
    description="Requires editor or admin role. Returns detailed information about a specific suggestion.",
)
async def get_suggestion_detail(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_editor_or_admin),
) -> dict[str, Any]:
    """Get detailed information about a specific suggestion."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        items = service.list_pending(table)
        item = next((i for i in items if i["id"] == suggestion_id), None)
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
    "/{category}/{suggestion_id}/approve",
    summary="Approve a suggestion",
    description="Requires editor or admin role. Marks a suggestion as approved and processes it for insertion into the main database.",
)
async def approve_suggestion(
    category: str,
    suggestion_id: int,
    request: Request,
    user: dict = Depends(require_editor_or_admin),
) -> dict[str, str]:
    """Approve a suggestion and process it for database insertion."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        # Import here to avoid circular dependencies
        from app.routes.moderation import (
            _approve_case_analyzer,
            _approve_default_category,
            nocodb_service,
            writer,
        )

        items = service.list_pending(table)
        item = next((i for i in items if i["id"] == suggestion_id), None)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or not pending",
            )

        original_payload: dict[str, Any] = item.get("payload") or {}

        # Get user email from Auth0 token
        moderator_email = user.get("https://cold.global/email") or user.get("email") or user.get("sub", "unknown")

        if category == "case-analyzer":
            # Use existing case analyzer approval logic
            await _approve_case_analyzer(request, table, suggestion_id, original_payload, item)
        else:
            # Use existing default category approval logic
            await _approve_default_category(request, category, table, suggestion_id, original_payload)

        return {"status": "success", "message": "Suggestion approved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve suggestion: {str(e)}",
        ) from e


@router.post(
    "/{category}/{suggestion_id}/reject",
    summary="Reject a suggestion",
    description="Requires editor or admin role. Marks a suggestion as rejected.",
)
async def reject_suggestion(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_editor_or_admin),
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
