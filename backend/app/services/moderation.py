"""Moderation decisions on submitted suggestions: approve into CoLD, or reject."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.config import config
from app.services.moderation_writer import MainDBWriter
from app.services.nocodb import NocoDBService
from app.services.suggestion_approval import approve_case_analyzer, normalize_domestic_instruments
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModerationCategory:
    """A moderation queue: its URL slug, suggestions table, display label and CoLD target table."""

    slug: str
    table: str
    label: str
    target_table: str | None


CASE_ANALYZER = ModerationCategory("case-analyzer", "case_analyzer", "Case Analyzer", None)

MODERATION_CATEGORIES: tuple[ModerationCategory, ...] = (
    CASE_ANALYZER,
    ModerationCategory("court-decisions", "court_decisions", "Court Decisions", "Court_Decisions"),
    ModerationCategory("domestic-instruments", "domestic_instruments", "Domestic Instruments", "Domestic_Instruments"),
    ModerationCategory("regional-instruments", "regional_instruments", "Regional Instruments", "Regional_Instruments"),
    ModerationCategory(
        "international-instruments",
        "international_instruments",
        "International Instruments",
        "International_Instruments",
    ),
    ModerationCategory("literature", "literature", "Literature", "Literature"),
)

_CATEGORIES_BY_SLUG = {category.slug: category for category in MODERATION_CATEGORIES}

RESERVED_PAYLOAD_FIELDS = frozenset(
    {
        "submitter_email",
        "submitter_comments",
        "official_source_pdf",
        "source_pdf",
        "attachment",
        "category",
        "edit_entity_id",
    }
)

CASE_ANALYZER_APPROVAL_NOTE = "Automatically inserted into Court_Decisions table via NocoDB API"


class UnknownCategoryError(LookupError):
    """Raised when a slug names no moderation category."""


def category_for_slug(slug: str) -> ModerationCategory:
    """Return the moderation category for a URL slug.

    Raises:
        UnknownCategoryError: the slug names no moderation category.
    """
    category = _CATEGORIES_BY_SLUG.get(slug)
    if category is None:
        raise UnknownCategoryError(f"Invalid category: {slug}")
    return category


def nocodb_from_config() -> NocoDBService:
    """Build a NocoDB client from application settings."""
    if not config.NOCODB_BASE_URL or not config.NOCODB_API_TOKEN:
        raise ValueError("NocoDB API credentials not configured")
    return NocoDBService(base_url=config.NOCODB_BASE_URL, api_token=config.NOCODB_API_TOKEN)


class ModerationService:
    """Records one moderation decision per suggestion.

    Each decision holds a lock on the suggestion row from the undecided check until the
    status is written, so concurrent decisions cannot both succeed, and a failed approval
    leaves the suggestion undecided for a retry.
    """

    def __init__(
        self,
        suggestions: SuggestionService,
        writer_factory: Callable[[], MainDBWriter] = MainDBWriter,
        nocodb_factory: Callable[[], NocoDBService] = nocodb_from_config,
    ) -> None:
        self._suggestions = suggestions
        self._writer_factory = writer_factory
        self._nocodb_factory = nocodb_factory

    def approve(self, slug: str, suggestion_id: int, moderator: str) -> int:
        """Insert an undecided suggestion into CoLD, mark it approved and return the new record id.

        Raises:
            UnknownCategoryError: the slug names no moderation category.
            SuggestionNotFoundError: the suggestion does not exist.
            SuggestionAlreadyModeratedError: the suggestion already has a decision.
        """
        category = category_for_slug(slug)
        with self._suggestions.lock_for_moderation(category.table, suggestion_id) as session:
            item = self._suggestions.get_suggestion_by_id(category.table, suggestion_id, session=session)
            if item is None:
                raise RuntimeError(f"Locked suggestion {suggestion_id} could not be read")
            if category.target_table is None:
                merged_id = approve_case_analyzer(
                    self._suggestions,
                    self._writer_factory(),
                    self._nocodb_factory(),
                    item,
                    session=session,
                )
                note = CASE_ANALYZER_APPROVAL_NOTE
            else:
                merged_id = self._insert_into_target(category.target_table, item.get("payload") or {})
                note = ""
            self._suggestions.mark_status(
                category.table,
                suggestion_id,
                "approved",
                moderator,
                note=note,
                merged_id=merged_id,
                session=session,
            )
        return merged_id

    def reject(self, slug: str, suggestion_id: int, moderator: str) -> None:
        """Mark an undecided suggestion as rejected.

        Raises:
            UnknownCategoryError: the slug names no moderation category.
            SuggestionNotFoundError: the suggestion does not exist.
            SuggestionAlreadyModeratedError: the suggestion already has a decision.
        """
        category = category_for_slug(slug)
        with self._suggestions.lock_for_moderation(category.table, suggestion_id) as session:
            self._suggestions.mark_status(category.table, suggestion_id, "rejected", moderator, note="", session=session)

    def _insert_into_target(self, target_table: str, payload: dict[str, Any]) -> int:
        record = {key: value for key, value in payload.items() if key not in RESERVED_PAYLOAD_FIELDS}
        if target_table == "Domestic_Instruments":
            normalize_domestic_instruments(record)
        writer = self._writer_factory()
        merged_id = writer.insert_record(target_table, record)
        for key in ("jurisdiction", "jurisdiction_link"):
            if record.get(key):
                try:
                    writer.link_jurisdictions(target_table, merged_id, record[key])
                except Exception as e:
                    logger.warning(
                        "Failed to link jurisdiction '%s' for %s record %s: %s",
                        record[key],
                        target_table,
                        merged_id,
                        str(e),
                    )
        return merged_id
