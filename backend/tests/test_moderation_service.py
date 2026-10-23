"""Tests for moderation decisions: one decision per suggestion, nothing recorded on failure."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.routes.suggestions import approve_suggestion, reject_suggestion
from app.services.moderation import CASE_ANALYZER_APPROVAL_NOTE, ModerationService, UnknownCategoryError
from app.services.moderation_writer import MainDBWriter
from app.services.suggestions import (
    SuggestionAlreadyModeratedError,
    SuggestionNotFoundError,
    SuggestionService,
    suggestions_db_manager,
)

MODERATOR = "editor@cold.global"


class FakeNocoDB:
    def __init__(self, fail_create: bool = False) -> None:
        self.fail_create = fail_create
        self.created: list[dict[str, Any]] = []
        self.links: list[dict[str, Any]] = []

    def list_jurisdictions(self, name: str) -> list[int]:
        return [5]

    def create_row(self, table_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if self.fail_create:
            raise RuntimeError("NocoDB unavailable")
        self.created.append(data)
        return {"Id": 77}

    def link_records(self, **kwargs: Any) -> None:
        self.links.append(kwargs)

    def upload_file(self, **kwargs: Any) -> None:
        raise AssertionError("no PDF is attached in these tests")


@pytest.fixture
def case_analyzer_table(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[sa.Engine, sa.Table]]:
    metadata = sa.MetaData()
    table = sa.Table(
        "suggestions_case_analyzer",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("username", sa.Text),
        sa.Column("model", sa.Text),
        sa.Column("case_citation", sa.Text),
        sa.Column("user_email", sa.Text),
        sa.Column("data", sa.JSON, nullable=False),
        sa.Column("analyzer", sa.JSON),
        sa.Column("submitted_data", sa.JSON),
        sa.Column("moderation_status", sa.String(32)),
    )
    engine = sa.create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    metadata.create_all(engine)

    @contextmanager
    def get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(suggestions_db_manager, "get_session", get_session)
    yield engine, table
    engine.dispose()


def _service_with(table: sa.Table) -> SuggestionService:
    service = SuggestionService.__new__(SuggestionService)
    service.tables = {"case_analyzer": table}
    return service


def _insert_analysis(engine: sa.Engine, table: sa.Table, **values: Any) -> None:
    row = {
        "id": 1,
        "data": {"file_name": "decision.pdf"},
        "submitted_data": {
            "abstract": "Abstract text.",
            "courts_position": "The court applied Swiss law.",
            "jurisdiction": "Switzerland",
            "raw_data": "{}",
        },
        "moderation_status": "pending",
        **values,
    }
    with engine.begin() as connection:
        connection.execute(table.insert().values(**row))


def _row(engine: sa.Engine, table: sa.Table) -> dict[str, Any]:
    with engine.connect() as connection:
        return dict(connection.execute(sa.select(table)).mappings().one())


def _moderation(service: SuggestionService, nocodb: FakeNocoDB) -> ModerationService:
    return ModerationService(
        service,
        writer_factory=lambda: MainDBWriter(sa.create_engine("sqlite://")),
        nocodb_factory=lambda: nocodb,  # type: ignore[arg-type, return-value]
    )


class TestCaseAnalyzerDecisions:
    def test_approve_creates_record_and_marks_approved(self, case_analyzer_table) -> None:
        engine, table = case_analyzer_table
        _insert_analysis(engine, table)
        nocodb = FakeNocoDB()

        merged_id = _moderation(_service_with(table), nocodb).approve("case-analyzer", 1, MODERATOR)

        assert merged_id == 77
        assert nocodb.created[0]["Abstract"] == "Abstract text."
        assert nocodb.links[0]["linked_record_ids"] == [5]
        row = _row(engine, table)
        assert row["moderation_status"] == "approved"
        assert row["data"]["moderated_by"] == MODERATOR
        assert row["data"]["merged_record_id"] == 77
        assert row["data"]["moderation_note"] == CASE_ANALYZER_APPROVAL_NOTE

    def test_legacy_payload_is_normalized_inside_the_decision(self, case_analyzer_table) -> None:
        engine, table = case_analyzer_table
        _insert_analysis(
            engine,
            table,
            submitted_data=None,
            data={"abstract": "Legacy abstract.", "precise_jurisdiction": "Switzerland"},
        )

        _moderation(_service_with(table), FakeNocoDB()).approve("case-analyzer", 1, MODERATOR)

        row = _row(engine, table)
        assert row["moderation_status"] == "approved"
        assert row["data"]["normalized"]["abstract"] == "Legacy abstract."

    def test_failed_approval_leaves_suggestion_pending(self, case_analyzer_table) -> None:
        engine, table = case_analyzer_table
        _insert_analysis(engine, table, submitted_data=None, data={"abstract": "Legacy abstract."})

        with pytest.raises(RuntimeError, match="NocoDB unavailable"):
            _moderation(_service_with(table), FakeNocoDB(fail_create=True)).approve("case-analyzer", 1, MODERATOR)

        row = _row(engine, table)
        assert row["moderation_status"] == "pending"
        assert "normalized" not in row["data"]

    def test_second_decision_is_refused(self, case_analyzer_table) -> None:
        engine, table = case_analyzer_table
        _insert_analysis(engine, table)
        moderation = _moderation(_service_with(table), FakeNocoDB())
        moderation.reject("case-analyzer", 1, MODERATOR)

        with pytest.raises(SuggestionAlreadyModeratedError) as approve_error:
            moderation.approve("case-analyzer", 1, MODERATOR)
        with pytest.raises(SuggestionAlreadyModeratedError):
            moderation.reject("case-analyzer", 1, MODERATOR)

        assert approve_error.value.status == "rejected"
        assert _row(engine, table)["moderation_status"] == "rejected"

    def test_missing_suggestion_is_not_found(self, case_analyzer_table) -> None:
        _, table = case_analyzer_table

        with pytest.raises(SuggestionNotFoundError):
            _moderation(_service_with(table), FakeNocoDB()).reject("case-analyzer", 404, MODERATOR)


class FakeSuggestions:
    """Records the calls a default-category decision makes on the suggestion store."""

    def __init__(self, payload: dict[str, Any], decided: str | None = None) -> None:
        self.payload = payload
        self.decided = decided
        self.calls: list[tuple[str, Any]] = []

    @contextmanager
    def lock_for_moderation(self, table: str, suggestion_id: int) -> Iterator[str]:
        if self.decided is not None:
            raise SuggestionAlreadyModeratedError(self.decided)
        self.calls.append(("lock", table))
        yield "locked-session"
        self.calls.append(("commit", table))

    def get_suggestion_by_id(self, table: str, suggestion_id: int, *, session: Any = None) -> dict[str, Any]:
        return {"id": suggestion_id, "payload": dict(self.payload)}

    def mark_status(self, table: str, suggestion_id: int, status: str, moderator: str, **kwargs: Any) -> None:
        self.calls.append(("mark", (status, kwargs.get("merged_id"), kwargs.get("session"))))


class FakeWriter:
    def __init__(self, fail_insert: bool = False) -> None:
        self.fail_insert = fail_insert
        self.inserted: list[tuple[str, dict[str, Any]]] = []
        self.linked: list[tuple[str, int, Any]] = []

    def insert_record(self, table_name: str, data: dict[str, Any]) -> int:
        if self.fail_insert:
            raise RuntimeError("insert failed")
        self.inserted.append((table_name, data))
        return 42

    def link_jurisdictions(self, table_name: str, record_id: int, value: Any) -> None:
        self.linked.append((table_name, record_id, value))


def _default_moderation(suggestions: FakeSuggestions, writer: FakeWriter) -> ModerationService:
    return ModerationService(
        suggestions,  # type: ignore[arg-type]
        writer_factory=lambda: writer,  # type: ignore[arg-type, return-value]
        nocodb_factory=lambda: pytest.fail("default categories do not use NocoDB"),
    )


class TestDefaultCategoryDecisions:
    def test_approve_inserts_without_reserved_fields_then_marks_in_the_locked_session(self) -> None:
        suggestions = FakeSuggestions(
            {
                "entry_into_force": "2019-01-01",
                "official_title": "PIL Act",
                "jurisdiction": "CHE",
                "submitter_email": "someone@example.com",
                "category": "domestic_instrument",
            }
        )
        writer = FakeWriter()

        merged_id = _default_moderation(suggestions, writer).approve("domestic-instruments", 3, MODERATOR)

        assert merged_id == 42
        table_name, record = writer.inserted[0]
        assert table_name == "Domestic_Instruments"
        assert record == {
            "entry_into_force": "2019-01-01",
            "official_title": "PIL Act",
            "jurisdiction": "CHE",
            "date_year_of_entry_into_force": "2019",
        }
        assert writer.linked == [("Domestic_Instruments", 42, "CHE")]
        assert suggestions.calls == [
            ("lock", "domestic_instruments"),
            ("mark", ("approved", 42, "locked-session")),
            ("commit", "domestic_instruments"),
        ]

    def test_failed_insert_records_no_decision(self) -> None:
        suggestions = FakeSuggestions({"title": "A book"})

        with pytest.raises(RuntimeError, match="insert failed"):
            _default_moderation(suggestions, FakeWriter(fail_insert=True)).approve("literature", 3, MODERATOR)

        assert suggestions.calls == [("lock", "literature")]

    def test_already_decided_suggestion_is_not_inserted(self) -> None:
        writer = FakeWriter()

        with pytest.raises(SuggestionAlreadyModeratedError):
            _default_moderation(FakeSuggestions({"title": "A book"}, decided="approved"), writer).approve(
                "literature", 3, MODERATOR
            )

        assert writer.inserted == []

    @pytest.mark.parametrize("slug", ["feedback", "generic", "nonsense"])
    def test_unknown_category(self, slug: str) -> None:
        with pytest.raises(UnknownCategoryError):
            _default_moderation(FakeSuggestions({}), FakeWriter()).reject(slug, 1, MODERATOR)


class FakeModeration:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def approve(self, slug: str, suggestion_id: int, moderator: str) -> int:
        if self.error:
            raise self.error
        return 1

    def reject(self, slug: str, suggestion_id: int, moderator: str) -> None:
        if self.error:
            raise self.error


EDITOR = {"https://cold.global/email": MODERATOR}


class TestDecisionRoutes:
    @pytest.mark.parametrize("route", [approve_suggestion, reject_suggestion])
    @pytest.mark.parametrize(
        ("error", "status_code"),
        [
            (SuggestionNotFoundError("missing"), 404),
            (SuggestionAlreadyModeratedError("approved"), 409),
            (RuntimeError("boom"), 500),
        ],
    )
    def test_errors_map_to_status_codes(self, route, error: Exception, status_code: int) -> None:
        with pytest.raises(HTTPException) as exc:
            route("literature", 1, user=EDITOR, moderation=FakeModeration(error))  # type: ignore[arg-type]
        assert exc.value.status_code == status_code

    @pytest.mark.parametrize("route", [approve_suggestion, reject_suggestion])
    def test_feedback_is_not_a_suggestion_category(self, route) -> None:
        with pytest.raises(HTTPException) as exc:
            route("feedback", 1, user=EDITOR, moderation=FakeModeration())  # type: ignore[arg-type]
        assert exc.value.status_code == 404

    def test_success(self) -> None:
        result = approve_suggestion("literature", 1, user=EDITOR, moderation=FakeModeration())  # type: ignore[arg-type]
        assert result.status == "success"
