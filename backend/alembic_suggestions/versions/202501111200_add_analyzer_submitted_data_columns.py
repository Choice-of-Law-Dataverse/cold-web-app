"""Add analyzer and submitted_data columns to suggestions_case_analyzer.

Revision ID: 202501111200
Revises: 202501041200
Create Date: 2026-01-11 12:00:00.000000

This migration adds structured columns to separate concerns:
- analyzer: JSONB column for AI analysis steps with reasoning/confidence (audit trail)
- submitted_data: JSONB column for user-submitted data for approval

The existing 'data' column is kept for backwards compatibility with old records.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op as alembic_op

revision = "202501111200"
down_revision = "202501041200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add analyzer column for AI analysis steps (audit trail)
    alembic_op.add_column(
        "suggestions_case_analyzer",
        sa.Column(
            "analyzer",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="AI analysis steps with reasoning and confidence scores",
        ),
    )

    # Add submitted_data column for user-submitted data
    alembic_op.add_column(
        "suggestions_case_analyzer",
        sa.Column(
            "submitted_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="User-edited data submitted for moderation approval",
        ),
    )


def downgrade() -> None:
    alembic_op.drop_column("suggestions_case_analyzer", "submitted_data")
    alembic_op.drop_column("suggestions_case_analyzer", "analyzer")
