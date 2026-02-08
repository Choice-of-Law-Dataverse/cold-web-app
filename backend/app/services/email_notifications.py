import logging
from typing import Any

import resend

from app.config import config

logger = logging.getLogger(__name__)

CATEGORY_LABELS: dict[str, str] = {
    "generic": "General Suggestion",
    "court_decisions": "Court Decision",
    "domestic_instruments": "Domestic Instrument",
    "regional_instruments": "Regional Instrument",
    "international_instruments": "International Instrument",
    "literature": "Literature",
}

CATEGORY_URL_SLUGS: dict[str, str] = {
    "generic": "generic",
    "court_decisions": "court-decisions",
    "domestic_instruments": "domestic-instruments",
    "regional_instruments": "regional-instruments",
    "international_instruments": "international-instruments",
    "literature": "literature",
    "feedback": "feedback",
}

ENTITY_TYPE_LABELS: dict[str, str] = {
    "court_decision": "Court Decision",
    "domestic_instrument": "Domestic Instrument",
    "regional_instrument": "Regional Instrument",
    "international_instrument": "International Instrument",
    "literature": "Literature",
    "arbitral_award": "Arbitral Award",
    "arbitral_rule": "Arbitral Rule",
    "question": "Question",
    "jurisdiction": "Jurisdiction",
}

FEEDBACK_TYPE_LABELS: dict[str, str] = {
    "improve": "Suggest Improvement",
    "missing_data": "Missing Data",
    "wrong_info": "Wrong Information",
    "outdated": "Outdated Information",
    "other": "Other",
}


def _get_admin_emails() -> list[str]:
    raw = config.ADMIN_NOTIFICATION_EMAILS
    if not raw:
        return []
    return [e.strip() for e in raw.split(",") if e.strip()]


def _extract_summary(category: str, payload: dict[str, Any]) -> str:
    if category == "court_decisions":
        return payload.get("case_citation") or payload.get("case_title") or "Unknown court decision"
    if category in ("domestic_instruments", "regional_instruments", "international_instruments"):
        return (
            payload.get("title")
            or payload.get("official_title")
            or payload.get("title_en")
            or payload.get("name")
            or payload.get("abbreviation")
            or "Unknown instrument"
        )
    if category == "literature":
        author = payload.get("author") or "Unknown author"
        title = payload.get("title") or "Unknown title"
        return f"{author} — {title}"
    return str(payload.get("data", payload))[:200]


def _build_moderation_url(category: str, suggestion_id: int) -> str:
    slug = CATEGORY_URL_SLUGS.get(category, category)
    return f"https://cold.global/moderation/{slug}/{suggestion_id}"


def _extract_user_email(user: dict[str, Any] | None) -> str | None:
    if not user:
        return None
    return user.get("https://cold.global/email") or user.get("email") or user.get("sub")


def send_new_suggestion_notification(
    category: str,
    suggestion_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] | None = None,
) -> None:
    if not config.RESEND_API_KEY:
        logger.debug("RESEND_API_KEY not configured — skipping email notification")
        return

    recipients = _get_admin_emails()
    if not recipients:
        logger.debug("ADMIN_NOTIFICATION_EMAILS not configured — skipping email notification")
        return

    resend.api_key = config.RESEND_API_KEY

    is_edit = bool(payload.get("edit_entity_id"))
    action = "Edit Suggestion" if is_edit else "New Suggestion"
    label = CATEGORY_LABELS.get(category, category)
    summary = _extract_summary(category, payload)
    moderation_url = _build_moderation_url(category, suggestion_id)
    submitter_email = payload.get("submitter_email") or _extract_user_email(user) or "Not provided"
    submitter_comments = payload.get("submitter_comments")

    subject = f"[CoLD] {action}: {label}"

    text_lines = [
        f"{action} submitted for review.",
        "",
        f"Category: {label}",
        f"Summary: {summary}",
        f"Submitter: {submitter_email}",
    ]
    if submitter_comments:
        text_lines.append(f"Comments: {submitter_comments}")
    if is_edit:
        text_lines.append(f"Editing entity: {payload['edit_entity_id']}")
    text_lines += [
        "",
        f"Review: {moderation_url}",
    ]
    text_body = "\n".join(text_lines)

    comments_html = f"<p><strong>Comments:</strong> {submitter_comments}</p>" if submitter_comments else ""
    edit_html = f"<p><strong>Editing entity:</strong> {payload['edit_entity_id']}</p>" if is_edit else ""
    html_body = f"""\
<h2>{action}: {label}</h2>
<p><strong>Summary:</strong> {summary}</p>
<p><strong>Submitter:</strong> {submitter_email}</p>
{comments_html}
{edit_html}
<p><a href="{moderation_url}">Review this suggestion</a></p>"""

    try:
        resend.Emails.send(
            {
                "from": config.NOTIFICATION_SENDER_EMAIL,
                "to": recipients,
                "subject": subject,
                "text": text_body,
                "html": html_body,
            }
        )
        logger.info("Notification email sent for %s suggestion #%d", category, suggestion_id)
    except Exception:
        logger.exception("Failed to send notification email for %s suggestion #%d", category, suggestion_id)


def send_feedback_notification(
    feedback_id: int,
    entity_type: str,
    entity_id: str,
    entity_title: str | None,
    feedback_type: str,
    message: str,
    submitter_email: str,
) -> None:
    if not config.RESEND_API_KEY:
        logger.debug("RESEND_API_KEY not configured — skipping feedback notification")
        return

    recipients = _get_admin_emails()
    if not recipients:
        logger.debug("ADMIN_NOTIFICATION_EMAILS not configured — skipping feedback notification")
        return

    resend.api_key = config.RESEND_API_KEY

    entity_label = ENTITY_TYPE_LABELS.get(entity_type, entity_type)
    feedback_label = FEEDBACK_TYPE_LABELS.get(feedback_type, feedback_type)
    title_display = entity_title or entity_id
    moderation_url = f"https://cold.global/moderation/feedback/{feedback_id}"
    entity_url = f"https://cold.global/{entity_type.replace('_', '-')}/{entity_id}"

    subject = f"[CoLD] Entity Feedback: {entity_label}"

    text_body = "\n".join(
        [
            f"New feedback submitted on a {entity_label}.",
            "",
            f"Entity: {title_display}",
            f"Entity URL: {entity_url}",
            f"Feedback type: {feedback_label}",
            f"Message: {message}",
            f"Submitter: {submitter_email}",
            "",
            f"Review: {moderation_url}",
        ]
    )

    html_body = f"""\
<h2>Entity Feedback: {entity_label}</h2>
<p><strong>Entity:</strong> <a href="{entity_url}">{title_display}</a></p>
<p><strong>Feedback type:</strong> {feedback_label}</p>
<p><strong>Message:</strong> {message}</p>
<p><strong>Submitter:</strong> {submitter_email}</p>
<p><a href="{moderation_url}">Review this feedback</a></p>"""

    try:
        resend.Emails.send(
            {
                "from": config.NOTIFICATION_SENDER_EMAIL,
                "to": recipients,
                "subject": subject,
                "text": text_body,
                "html": html_body,
            }
        )
        logger.info("Feedback notification email sent for feedback #%d", feedback_id)
    except Exception:
        logger.exception("Failed to send feedback notification email for #%d", feedback_id)
