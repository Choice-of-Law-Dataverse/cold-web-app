import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from app.auth import optional_user, require_editor_or_admin, verify_frontend_request
from app.schemas.feedback import FeedbackDetail, FeedbackResponse, FeedbackSubmit, FeedbackUpdate
from app.services.email_notifications import send_feedback_notification
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    dependencies=[Depends(verify_frontend_request)],
)


def _get_service() -> SuggestionService:
    return SuggestionService()


def _extract_email(user: dict | None) -> str | None:
    if not user:
        return None
    return user.get("https://cold.global/email") or user.get("email") or user.get("sub")


@router.post(
    "",
    summary="Submit entity feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_feedback(
    body: FeedbackSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict | None = Depends(optional_user),
    service: SuggestionService = Depends(_get_service),
) -> FeedbackResponse:
    token_sub = _extract_email(user) if user else None
    try:
        new_id = service.save_entity_feedback(
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            entity_title=body.entity_title,
            feedback_type=body.feedback_type,
            message=body.message,
            submitter_email=body.submitter_email,
            token_sub=token_sub,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
        )
        background_tasks.add_task(
            send_feedback_notification,
            new_id,
            body.entity_type,
            body.entity_id,
            body.entity_title,
            body.feedback_type,
            body.message,
            body.submitter_email,
        )
        return FeedbackResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/pending",
    summary="List pending feedback",
)
async def list_pending(
    _: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(_get_service),
) -> list[dict]:
    return service.list_pending_feedback()


@router.get(
    "/{feedback_id}",
    summary="Get feedback detail",
    response_model=FeedbackDetail,
)
async def get_feedback(
    feedback_id: int,
    _: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(_get_service),
) -> FeedbackDetail:
    record = service.get_feedback_by_id(feedback_id)
    if not record:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackDetail(**record)


@router.patch(
    "/{feedback_id}",
    summary="Update feedback status",
)
async def update_feedback(
    feedback_id: int,
    body: FeedbackUpdate,
    _: dict = Depends(require_editor_or_admin),
    service: SuggestionService = Depends(_get_service),
) -> dict:
    updated = service.update_feedback_status(feedback_id, body.moderation_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"status": "ok", "message": f"Feedback #{feedback_id} marked as {body.moderation_status}"}
