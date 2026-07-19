"""Regression tests for case-analyzer persistence."""

from collections.abc import Iterator
from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.services.suggestions import SuggestionService, suggestions_db_manager


def test_case_citation_step_keeps_json_and_search_column_synchronized(monkeypatch) -> None:
    metadata = sa.MetaData()
    table = sa.Table(
        "case_analyzer",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_citation", sa.Text),
        sa.Column("analyzer", sa.JSON),
    )
    engine = sa.create_engine("sqlite://")
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            table.insert().values(
                id=1,
                case_citation="old citation",
                analyzer={"themes": {"themes": ["Contracts"]}},
            )
        )

    @contextmanager
    def get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(suggestions_db_manager, "get_session", get_session)
    service = SuggestionService.__new__(SuggestionService)
    service.tables = {"case_analyzer": table}

    citation_step = {
        "case_citation": "  4A_305/2025  ",
        "source_text": "4A_305_2025 13.03.2026.pdf",
        "source_location": "original filename",
        "identifier_type": "docket number",
        "confidence": "medium",
        "reasoning": "The filename encodes the docket number.",
    }
    service.update_analyzer_step(1, "case_citation", citation_step)

    with engine.connect() as connection:
        row = connection.execute(sa.select(table)).mappings().one()
    assert row["case_citation"] == "4A_305/2025"
    assert row["analyzer"]["case_citation"] == citation_step
    assert row["analyzer"]["themes"] == {"themes": ["Contracts"]}

    service.update_analyzer_step(1, "themes", {"themes": ["Torts"]})
    with engine.connect() as connection:
        row = connection.execute(sa.select(table)).mappings().one()
    assert row["case_citation"] == "4A_305/2025"

    service.update_analyzer_step(1, "case_citation", {"case_citation": "NA", "confidence": "low"})
    with engine.connect() as connection:
        row = connection.execute(sa.select(table)).mappings().one()
    assert row["case_citation"] is None
    assert row["analyzer"]["case_citation"] == {"case_citation": "NA", "confidence": "low"}
