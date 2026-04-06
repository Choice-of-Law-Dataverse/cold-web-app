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
from app.services.moderation_writer import MainDBWriter
from app.services.suggestion_approval import (
    approve_case_analyzer,
    get_target_table,
    link_jurisdictions_for_default_categories,
    normalize_domestic_instruments,
)
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)

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


_CATEGORIES: dict[str, tuple[str, str]] = {
    "case_analyzer": ("case-analyzer", "Case Analyzer"),
    "court_decisions": ("court-decisions", "Court Decisions"),
    "domestic_instruments": ("domestic-instruments", "Domestic Instruments"),
    "regional_instruments": ("regional-instruments", "Regional Instruments"),
    "international_instruments": ("international-instruments", "International Instruments"),
    "literature": ("literature", "Literature"),
    "feedback": ("feedback", "Entity Feedback"),
}

_SLUG_TO_TABLE: dict[str, str] = {slug: table for table, (slug, _) in _CATEGORIES.items()}


def _table_key(path_segment: str) -> str | None:
    """Map category path segment to internal table name."""
    return _SLUG_TO_TABLE.get(path_segment)


@router.get(
    "/moderation/summary",
    summary="Get pending counts for all moderation categories",
    description="Requires editor or admin role. Returns pending suggestion counts per category.",
)
async def moderation_summary(
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> list[ModerationSummaryItem]:
    try:
        counts = service.count_pending_by_category()
        return [
            ModerationSummaryItem(
                category=meta[0],
                label=meta[1],
                pending_count=counts.get(table, 0),
            )
            for table, meta in _CATEGORIES.items()
            if table != "feedback"
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
    summary="List pending suggestions for a category",
    description="Requires editor or admin role. Returns list of pending suggestions for moderation.",
)
async def list_pending_suggestions(
    category: str,
    show_all: bool = False,
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> list[PendingSuggestionItem]:
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )
    try:
        if category == "case-analyzer":
            if show_all:
                rows = service.list_all_case_analyzer()
            else:
                rows = service.list_pending_case_analyzer()
        else:
            rows = service.list_pending(table)
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
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    is_moderator = has_editor_access(user)

    if not is_moderator and table == "case_analyzer":
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
    description="Requires editor or admin role. Marks a suggestion as approved and processes it for insertion",
)
async def approve_suggestion(
    category: str,
    suggestion_id: int,
    request: Request,
    user: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> StatusMessage:
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        if category == "case-analyzer":
            item = service.get_suggestion_by_id(table, suggestion_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Suggestion not found",
                )
            item_status = item.get("moderation_status")
            if item_status in {"approved", "rejected"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Suggestion already {item_status}",
                )
        else:
            item = service.get_suggestion_by_id(table, suggestion_id, pending_only=True)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Suggestion not found or not pending",
                )

        original_payload: dict[str, Any] = item.get("payload", {}) or {}

        # Get user email from Auth0 token
        moderator_email = extract_user_identity(user) or "unknown"

        if category == "case-analyzer":
            writer = MainDBWriter()
            await approve_case_analyzer(service, writer, table, suggestion_id, original_payload, item, moderator_email)
        else:
            # Handle default categories - simplified without form editing
            writer = MainDBWriter()
            target_table = get_target_table(category)
            if not target_table:
                raise HTTPException(status_code=400, detail="Unsupported category")

            if target_table == "Domestic_Instruments":
                normalize_domestic_instruments(original_payload)

            # Filter out reserved metadata fields
            _reserved = {
                "submitter_email",
                "submitter_comments",
                "official_source_pdf",
                "source_pdf",
                "attachment",
                "category",
                "edit_entity_id",
            }
            payload_for_writer = {k: v for k, v in original_payload.items() if k not in _reserved}

            merged_id = writer.insert_record(target_table, payload_for_writer)
            link_jurisdictions_for_default_categories(writer, target_table, merged_id, payload_for_writer)

            service.mark_status(
                table,
                suggestion_id,
                "approved",
                moderator_email,
                note="",
                merged_id=merged_id,
            )

        return StatusMessage(status="success", message="Suggestion approved successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to approve suggestion category=%s id=%d", category, suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve suggestion",
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
    service: SuggestionService = Depends(get_suggestion_service),
) -> StatusMessage:
    """Reject a suggestion."""
    table = _table_key(category)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category: {category}",
        )

    try:
        # Get user email from Auth0 token
        moderator_email = extract_user_identity(user) or "unknown"

        service.mark_status(
            table,
            suggestion_id,
            "rejected",
            moderator_email,
            note="",
        )

        return StatusMessage(status="success", message="Suggestion rejected successfully")

    except Exception as e:
        logger.exception("Failed to reject suggestion category=%s id=%d", category, suggestion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject suggestion",
        ) from e


@router.delete(
    "/{category}/{suggestion_id}",
    summary="Delete a suggestion",
    description="Requires editor or admin role. Permanently deletes a suggestion.",
)
async def delete_suggestion(
    category: str,
    suggestion_id: int,
    _: dict[str, Any] = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(get_suggestion_service),
) -> StatusMessage:
    """Delete a suggestion permanently."""
    if category != "case-analyzer":
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
