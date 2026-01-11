"""Backfill moderation_status column from data JSON for case_analyzer.

Revision ID: 202501111300
Revises: 202501111200
Create Date: 2026-01-11 13:00:00.000000

This migration populates the moderation_status column from the data JSONB column
for records where moderation_status is NULL. This ensures backwards compatibility
with old records that stored status inside the data JSON.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op as alembic_op

revision = "202501111300"
down_revision = "202501111200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill moderation_status from data->>'moderation_status' where column is NULL
    alembic_op.execute(
        sa.text("""
            UPDATE suggestions_case_analyzer
            SET moderation_status = COALESCE(moderation_status, data->>'moderation_status', data->>'status', 'pending')
            WHERE moderation_status IS NULL
        """)
    )


def downgrade() -> None:
    # No downgrade needed - we're just populating data, not changing schema
    pass
