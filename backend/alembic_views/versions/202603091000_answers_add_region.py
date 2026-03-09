from __future__ import annotations

import os

from alembic import op

revision = "202603091000"
down_revision = "202603081200"
branch_labels = None
depends_on = None

SCHEMA = os.environ.get("NOCODB_POSTGRES_SCHEMA", "p1q5x3pj29vkrdr")


def _base_answers_sql(*, with_region: bool) -> str:
    region_col = '\n    jcodes."Region" AS jurisdictions_region' if with_region else ""
    lateral_cols = 'j."Alpha_3_Code", j."Region"' if with_region else 'j."Alpha_3_Code"'
    return f"""
CREATE OR REPLACE VIEW data_views.base_answers AS
SELECT
    a.id,
    a."Answer" AS answer,
    a."More_Information" AS more_information,
    a."To_Review_" AS to_review,
    a."OUP_Book_Quote" AS oup_book_quote,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    qcold."CoLD_ID" AS question_cold_id,
    (COALESCE(jcodes."Alpha_3_Code", '') || '_' || COALESCE(qcold."CoLD_ID", '')) AS cold_id,
    a.created_at,
    a.updated_at,
    a.created_by,
    a.updated_by{"," + region_col if with_region else ""}
FROM {SCHEMA}."Answers" a
LEFT JOIN LATERAL (
    SELECT {lateral_cols}
    FROM {SCHEMA}."_nc_m2m_Jurisdictions_Answers" ja
    JOIN {SCHEMA}."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
    WHERE ja."Answers_id" = a.id
    ORDER BY j.id
    LIMIT 1
) jcodes ON true
LEFT JOIN LATERAL (
    SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_Questions_Answers" qa
    JOIN {SCHEMA}."Questions" q ON q.id = qa."Questions_id"
    WHERE qa."Answers_id" = a.id
    ORDER BY q.id
    LIMIT 1
) qcold ON true;
"""


def upgrade() -> None:
    op.execute(_base_answers_sql(with_region=True))


def downgrade() -> None:
    op.execute(_base_answers_sql(with_region=False))
