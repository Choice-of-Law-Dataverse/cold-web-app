"""Shared SQLAlchemy metadata for suggestion tables.

This module exposes a single metadata instance and per-table definitions so both the
runtime service layer and Alembic migrations operate on the same schema description.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

SUGGESTIONS_METADATA = sa.MetaData()


def _timestamp_column(*, timezone: bool = True, server_default: str = "now()") -> sa.Column:
    """Create a timestamp column with consistent defaults."""
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=timezone),
        server_default=sa.text(server_default),
        nullable=False,
    )


suggestions_generic = sa.Table(
    "suggestions_generic",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_court_decisions = sa.Table(
    "suggestions_court_decisions",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_domestic_instruments = sa.Table(
    "suggestions_domestic_instruments",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_regional_instruments = sa.Table(
    "suggestions_regional_instruments",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_international_instruments = sa.Table(
    "suggestions_international_instruments",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_literature = sa.Table(
    "suggestions_literature",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(),
    sa.Column("payload", JSONB, nullable=False),
    sa.Column("client_ip", sa.String(64)),
    sa.Column("user_agent", sa.Text),
    sa.Column("source", sa.String(256)),
    sa.Column("token_sub", sa.String(256)),
    sa.Column("moderation_status", sa.String(32)),
)

suggestions_case_analyzer = sa.Table(
    "suggestions_case_analyzer",
    SUGGESTIONS_METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    _timestamp_column(timezone=False, server_default="CURRENT_TIMESTAMP"),
    sa.Column("username", sa.Text),
    sa.Column("model", sa.Text),
    sa.Column("case_citation", sa.Text),
    sa.Column("user_email", sa.Text),
    sa.Column("data", JSONB, nullable=False),
    sa.Column("moderation_status", sa.String(32)),
)

SUGGESTION_TABLES: dict[str, sa.Table] = {
    "generic": suggestions_generic,
    "court_decisions": suggestions_court_decisions,
    "domestic_instruments": suggestions_domestic_instruments,
    "regional_instruments": suggestions_regional_instruments,
    "international_instruments": suggestions_international_instruments,
    "literature": suggestions_literature,
    "case_analyzer": suggestions_case_analyzer,
}

SUGGESTION_TABLE_NAMES = tuple(SUGGESTION_TABLES.keys())


sa.Index("idx_suggestions_generic_moderation_status", suggestions_generic.c.moderation_status)
sa.Index(
    "idx_suggestions_court_decisions_moderation_status",
    suggestions_court_decisions.c.moderation_status,
)
sa.Index(
    "idx_suggestions_domestic_instruments_moderation_status",
    suggestions_domestic_instruments.c.moderation_status,
)
sa.Index(
    "idx_suggestions_regional_instruments_moderation_status",
    suggestions_regional_instruments.c.moderation_status,
)
sa.Index(
    "idx_suggestions_international_instruments_moderation_status",
    suggestions_international_instruments.c.moderation_status,
)
sa.Index("idx_suggestions_literature_moderation_status", suggestions_literature.c.moderation_status)
sa.Index("idx_suggestions_case_analyzer_moderation_status", suggestions_case_analyzer.c.moderation_status)
