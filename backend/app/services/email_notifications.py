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


def send_new_suggestion_notification(
    category: str,
    suggestion_id: int,
    payload: dict[str, Any],
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
    submitter_email = payload.get("submitter_email", "Not provided")
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
