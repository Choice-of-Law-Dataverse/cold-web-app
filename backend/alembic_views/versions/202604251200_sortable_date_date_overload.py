from __future__ import annotations

from alembic import op

revision = "202604251200"
down_revision = "202604251100"
branch_labels = None
depends_on = None


SORTABLE_DATE_DATE_OVERLOAD = """
CREATE OR REPLACE FUNCTION data_views._sortable_date(d DATE) RETURNS DATE AS $func$
BEGIN
    RETURN d;
END;
$func$ LANGUAGE plpgsql IMMUTABLE;
"""


DROP_SORTABLE_DATE_DATE_OVERLOAD = """
DROP FUNCTION IF EXISTS data_views._sortable_date(DATE);
"""


def upgrade() -> None:
    op.execute(SORTABLE_DATE_DATE_OVERLOAD)


def downgrade() -> None:
    op.execute(DROP_SORTABLE_DATE_DATE_OVERLOAD)
