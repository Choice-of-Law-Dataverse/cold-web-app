"""Create suggestion tables managed by Alembic.

Revision ID: 202501041200
Revises:
Create Date: 2026-01-04 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op as alembic_op

revision = "202501041200"
down_revision = None
branch_labels = None
depends_on = None


TIMESTAMPTZ_DEFAULT = sa.text("now()")


def upgrade() -> None:
    alembic_op.create_table(
        "suggestions_generic",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_generic_moderation_status",
        "suggestions_generic",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_court_decisions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_court_decisions_moderation_status",
        "suggestions_court_decisions",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_domestic_instruments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_domestic_instruments_moderation_status",
        "suggestions_domestic_instruments",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_regional_instruments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_regional_instruments_moderation_status",
        "suggestions_regional_instruments",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_international_instruments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_international_instruments_moderation_status",
        "suggestions_international_instruments",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_literature",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("source", sa.String(length=256)),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_literature_moderation_status",
        "suggestions_literature",
        ["moderation_status"],
    )

    alembic_op.create_table(
        "suggestions_case_analyzer",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("username", sa.Text()),
        sa.Column("model", sa.Text()),
        sa.Column("case_citation", sa.Text()),
        sa.Column("user_email", sa.Text()),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("moderation_status", sa.String(length=32)),
    )
    alembic_op.create_index(
        "idx_suggestions_case_analyzer_moderation_status",
        "suggestions_case_analyzer",
        ["moderation_status"],
    )


def downgrade() -> None:
    alembic_op.drop_index(
        "idx_suggestions_case_analyzer_moderation_status",
        table_name="suggestions_case_analyzer",
    )
    alembic_op.drop_table("suggestions_case_analyzer")

    alembic_op.drop_index(
        "idx_suggestions_literature_moderation_status",
        table_name="suggestions_literature",
    )
    alembic_op.drop_table("suggestions_literature")

    alembic_op.drop_index(
        "idx_suggestions_international_instruments_moderation_status",
        table_name="suggestions_international_instruments",
    )
    alembic_op.drop_table("suggestions_international_instruments")

    alembic_op.drop_index(
        "idx_suggestions_regional_instruments_moderation_status",
        table_name="suggestions_regional_instruments",
    )
    alembic_op.drop_table("suggestions_regional_instruments")

    alembic_op.drop_index(
        "idx_suggestions_domestic_instruments_moderation_status",
        table_name="suggestions_domestic_instruments",
    )
    alembic_op.drop_table("suggestions_domestic_instruments")

    alembic_op.drop_index(
        "idx_suggestions_court_decisions_moderation_status",
        table_name="suggestions_court_decisions",
    )
    alembic_op.drop_table("suggestions_court_decisions")

    alembic_op.drop_index(
        "idx_suggestions_generic_moderation_status",
        table_name="suggestions_generic",
    )
    alembic_op.drop_table("suggestions_generic")
