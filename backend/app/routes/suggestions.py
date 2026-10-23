import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status

from app.auth import extract_user_identity, has_editor_access, require_editor_or_admin, require_user, verify_frontend_request
from app.schemas.responses import ModerationSummaryItem, PendingSuggestionItem, StatusMessage, SuggestionDetailItem
from app.schemas.suggestions import (
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
    RegionalInstrumentSuggestion,
    SuggestionPayload,
    SuggestionResponse,
)
from app.services.email_notifications import send_new_suggestion_notification
from app.services.moderation import (
    CASE_ANALYZER,
    MODERATION_CATEGORIES,
    ModerationCategory,
    ModerationService,
    UnknownCategoryError,
    category_for_slug,
)
from app.services.suggestions import SuggestionAlreadyModeratedError, SuggestionNotFoundError, SuggestionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suggestions",
    tags=["Suggestions"],
    dependencies=[Depends(verify_frontend_request)],
)


def get_suggestion_service() -> SuggestionService:
    return SuggestionService()


def get_moderation_service(
    suggestions: SuggestionService = Depends(get_suggestion_service),
) -> ModerationService:
    return ModerationService(suggestions)


@router.post(
    "/",
    summary="Submit a new data suggestion (generic)",
    description=(
        "Submit a free-form data contribution for moderator review. The payload is stored as-is "
        "in a separate suggestions table. Use the typed endpoints below (court-decisions, "
        "domestic-instruments, etc.) for structured submissions. Requires authentication."
    ),
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_suggestion(
    body: SuggestionPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
) -> SuggestionResponse:
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
        background_tasks.add_task(send_new_suggestion_notification, "generic", new_id, payload, user)
        return SuggestionResponse(id=new_id)
    except Exception as e:
        logger.exception("Failed to save generic suggestion source=%s", body.source)
        raise HTTPException(status_code=500, detail="Failed to save suggestion") from e


_TYPED_SUGGESTION_ROUTES: list[tuple[str, str, str, str, type]] = [
    ("/court-decisions", "Court Decision", "court_decision", "court_decisions", CourtDecisionSuggestion),
    (
        "/domestic-instruments",
        "Domestic Instrument",
        "domestic_instrument",
        "domestic_instruments",
        DomesticInstrumentSuggestion,
    ),
    (
        "/regional-instruments",
        "Regional Instrument",
        "regional_instrument",
        "regional_instruments",
        RegionalInstrumentSuggestion,
    ),
    (
        "/international-instruments",
        "International Instrument",
        "international_instrument",
        "international_instruments",
        InternationalInstrumentSuggestion,
    ),
    ("/literature", "Literature", "literature", "literature", LiteratureSuggestion),
]


def _make_typed_handler(category: str, table: str, body_type: type):  # noqa: ANN202
    async def handler(
        body: body_type,  # type: ignore[valid-type]
        request: Request,
        background_tasks: BackgroundTasks,
        user: dict[str, Any] = Depends(require_user),
        source: str | None = Header(None),
        service: SuggestionService = Depends(get_suggestion_service),
    ) -> SuggestionResponse:
        try:
            payload = {"category": category, **body.model_dump()}
            new_id = service.save_suggestion(
                payload=payload,
                table=table,
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
                source=source,
                user=user,
            )
            background_tasks.add_task(send_new_suggestion_notification, table, new_id, payload, user)
            return SuggestionResponse(id=new_id)
        except Exception as e:
            logger.exception("Failed to save suggestion category=%s table=%s", category, table)
            raise HTTPException(status_code=500, detail="Failed to save suggestion") from e

    return handler


for _path, _label, _category, _table, _body_type in _TYPED_SUGGESTION_ROUTES:
    _handler = _make_typed_handler(_category, _table, _body_type)
    router.add_api_route(
        _path,
        _handler,
        methods=["POST"],
        summary=f"Submit a new {_label} suggestion",
        response_model=SuggestionResponse,
        status_code=status.HTTP_201_CREATED,
    )


# Moderation endpoints


def _category_or_404(slug: str) -> ModerationCategory:
    try:
        return category_for_slug(slug)
    except UnknownCategoryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "/moderation/summary",
    summary="Moderation queue summary",
    description=(
        "Returns the number of pending suggestions in each moderation category "
        "(court decisions, instruments, literature, case analyzer, feedback). "
        "Requires editor or admin role."
    ),
)
async def moderation_summary(
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> list[ModerationSummaryItem]:
    try:
        counts = service.count_pending_by_category()
        return [
            ModerationSummaryItem(
                category=category.slug,
                label=category.label,
                pending_count=counts.get(category.table, 0),
            )
            for category in MODERATION_CATEGORIES
        ] + [
            ModerationSummaryItem(
                category="feedback",
                label="Entity Feedback",
                pending_count=counts.get("feedback", 0),
            )
        ]
    except Exception as e:
        logger.exception("Failed to fetch moderation summary for user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch moderation summary",
        ) from e


@router.get(
    "/pending/{category}",
    summary="List pending suggestions in a category",
    description=(
        "Returns all pending suggestions for the specified category slug. "
        "For `case-analyzer`, set `show_all=true` to include non-pending items. "
        "Requires editor or admin role.\n\n"
        "**Category slugs:** `case-analyzer`, `court-decisions`, `domestic-instruments`, "
        "`regional-instruments`, `international-instruments`, `literature`. "
        "Entity feedback has its own endpoints under `/feedback`."
    ),
)
async def list_pending_suggestions(
    category: str,
    show_all: bool = False,
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> list[PendingSuggestionItem]:
    moderation_category = _category_or_404(category)
    try:
        if moderation_category == CASE_ANALYZER:
            if show_all:
                rows = service.list_all_case_analyzer()
            else:
                rows = service.list_pending_case_analyzer()
        else:
            rows = service.list_pending(moderation_category.table)
        return [PendingSuggestionItem(**r) for r in rows]
    except Exception as e:
        logger.exception("Failed to fetch pending suggestions category=%s", category)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending suggestions",
        ) from e


@router.get(
    "/{category}/{suggestion_id}",
    summary="Get specific suggestion details",
    description=(
        "Authenticated users can retrieve details for their own submissions. "
        "Editors and admins can access any suggestion for moderation."
    ),
)
async def get_suggestion_detail(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_user),
    service: SuggestionService = Depends(get_suggestion_service),
) -> SuggestionDetailItem:
    table = _category_or_404(category).table

    is_moderator = has_editor_access(user)

    if not is_moderator and table == CASE_ANALYZER.table:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this category",
        )

    token_sub = None if is_moderator else extract_user_identity(user)
    if not is_moderator and not token_sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to verify submission ownership",
        )

    try:
        item = service.get_suggestion_by_id(table, suggestion_id, token_sub=token_sub)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or not accessible",
            )
        if not is_moderator:
            item.pop("token_sub", None)
        return SuggestionDetailItem(**item)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch suggestion category=%s id=%d", category, suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch suggestion",
        ) from e


@router.post(
    "/{category}/{suggestion_id}/approve",
    summary="Approve a suggestion",
    description=(
        "Mark a suggestion as approved and insert its data into the main CoLD database. "
        "For case-analyzer suggestions, this runs the full approval pipeline. "
        "For other categories, the payload is written directly to the target table. "
        "Returns 404 when the suggestion does not exist and 409 when it was already approved or rejected; "
        "a failed approval leaves the suggestion pending. Requires editor or admin role."
    ),
)
def approve_suggestion(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_editor_or_admin),
    moderation: ModerationService = Depends(get_moderation_service),
) -> StatusMessage:
    _category_or_404(category)
    moderator_email = extract_user_identity(user) or "unknown"
    try:
        moderation.approve(category, suggestion_id, moderator_email)
    except SuggestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found") from e
    except SuggestionAlreadyModeratedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to approve suggestion category=%s id=%d", category, suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve suggestion",
        ) from e
    return StatusMessage(status="success", message="Suggestion approved successfully")


@router.post(
    "/{category}/{suggestion_id}/reject",
    summary="Reject a suggestion",
    description=(
        "Mark a pending suggestion as rejected. The record is preserved for audit but not inserted into CoLD. "
        "Returns 404 when the suggestion does not exist and 409 when it was already approved or rejected. "
        "Requires editor or admin role."
    ),
)
def reject_suggestion(
    category: str,
    suggestion_id: int,
    user: dict = Depends(require_editor_or_admin),
    moderation: ModerationService = Depends(get_moderation_service),
) -> StatusMessage:
    _category_or_404(category)
    moderator_email = extract_user_identity(user) or "unknown"
    try:
        moderation.reject(category, suggestion_id, moderator_email)
    except SuggestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found") from e
    except SuggestionAlreadyModeratedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to reject suggestion category=%s id=%d", category, suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject suggestion",
        ) from e
    return StatusMessage(status="success", message="Suggestion rejected successfully")


@router.delete(
    "/{category}/{suggestion_id}",
    summary="Delete a suggestion",
    description="Permanently remove a suggestion. Only supported for the `case-analyzer` category. Requires editor or admin role.",
)
async def delete_suggestion(
    category: str,
    suggestion_id: int,
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> StatusMessage:
    if category != CASE_ANALYZER.slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delete is only supported for case-analyzer",
        )

    try:
        deleted = service.delete_case_analyzer(suggestion_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found",
            )

        return StatusMessage(status="success", message="Suggestion deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete suggestion id=%d", suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete suggestion",
        ) from e
