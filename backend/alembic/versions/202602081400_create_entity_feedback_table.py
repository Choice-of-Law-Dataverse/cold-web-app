"""Create entity_feedback table for lightweight user feedback on entities.

Revision ID: 202602081400
Revises: 202501111300
Create Date: 2026-02-08 14:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op as alembic_op

revision = "202602081400"
down_revision = "202501111300"
branch_labels = None
depends_on = None

TIMESTAMPTZ_DEFAULT = sa.text("now()")


def upgrade() -> None:
    alembic_op.create_table(
        "entity_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=TIMESTAMPTZ_DEFAULT, nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=256), nullable=False),
        sa.Column("entity_title", sa.String(length=512)),
        sa.Column("feedback_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("submitter_email", sa.String(length=256), nullable=False),
        sa.Column("token_sub", sa.String(length=256)),
        sa.Column("client_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("moderation_status", sa.String(length=32), server_default="pending", nullable=False),
    )
    alembic_op.create_index("idx_entity_feedback_moderation_status", "entity_feedback", ["moderation_status"])
    alembic_op.create_index("idx_entity_feedback_entity_type", "entity_feedback", ["entity_type"])
    alembic_op.create_index("idx_entity_feedback_entity_id", "entity_feedback", ["entity_id"])


def downgrade() -> None:
    alembic_op.drop_index("idx_entity_feedback_entity_id", table_name="entity_feedback")
    alembic_op.drop_index("idx_entity_feedback_entity_type", table_name="entity_feedback")
    alembic_op.drop_index("idx_entity_feedback_moderation_status", table_name="entity_feedback")
    alembic_op.drop_table("entity_feedback")
