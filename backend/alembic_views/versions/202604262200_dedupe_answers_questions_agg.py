"""Dedupe ``Questions`` aggregation in ``data_views.answers``.

The original ``questions_agg`` CTE (revision ``202603071000``) joined
``Questions`` to ``_nc_m2m_Themes_Questions`` and ``Themes`` inside the same
aggregation. Each question with N themes was therefore multiplied N times
before ``STRING_AGG(q."Question", ' | ')``, so the materialized ``Questions``
column repeated the same question text N times joined by `` | ``. The search
endpoint reads that column verbatim into the ``question`` field of the search
result, which is why QUESTION rows on the search results page show the same
question text duplicated and joined with `` | ``.

This migration splits theme aggregation into its own CTE -- mirroring the
pattern used for ``data_views.court_decisions`` in revision ``202604261800``
-- so the question text is aggregated exactly once per related question while
the themes column keeps its existing semantics.

The view's column list (names, order, and types) is unchanged, so dependent
plpgsql functions (``data_views.search_all_v2``, ``data_views.get_entity_detail``)
keep working without modification.
"""

from __future__ import annotations

from alembic import op

revision = "202604262200"
down_revision = "202604261900"
branch_labels = None
depends_on = None

SCHEMA = "p1q5x3pj29vkrdr"
S = SCHEMA


ANSWERS_MV_FIXED = f"""
DROP MATERIALIZED VIEW IF EXISTS data_views.answers CASCADE;
CREATE MATERIALIZED VIEW data_views.answers AS
WITH jurisdiction_agg AS (
    SELECT
        m2m."Answers_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions",
        STRING_AGG(j."Legal_Family", ' | ' ORDER BY j."Legal_Family") AS "Legal_Families",
        MIN(j."Alpha_3_Code") AS "Alpha_3_Code"
    FROM {S}."_nc_m2m_Jurisdictions_Answers" m2m
    JOIN {S}."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Answers_id"
),
questions_agg AS (
    SELECT
        m2m."Answers_id",
        STRING_AGG(q."Question", ' | ' ORDER BY q.id) AS "Questions",
        MIN(q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM {S}."_nc_m2m_Questions_Answers" m2m
    JOIN {S}."Questions" q ON q.id = m2m."Questions_id"
    GROUP BY m2m."Answers_id"
),
themes_agg AS (
    SELECT
        m2m."Answers_id",
        STRING_AGG(DISTINCT t."Theme", ' | ' ORDER BY t."Theme") AS "Themes"
    FROM {S}."_nc_m2m_Questions_Answers" m2m
    JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = m2m."Questions_id"
    JOIN {S}."Themes" t ON t.id = tq."Themes_id"
    GROUP BY m2m."Answers_id"
)
SELECT
    a.id,
    a."Answer",
    a."More_Information",
    'Answers Answer Response' AS "Table_Synonyms",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(ja."Legal_Families", '') AS "Legal_Families",
    COALESCE(qa."Questions", '') AS "Questions",
    COALESCE(ta."Themes", '') AS "Themes",
    (COALESCE(ja."Alpha_3_Code",'') || '_' || COALESCE(qa."CoLD_ID",'')) AS "CoLD_ID",
    a."updated_at"::date AS sort_date,
    to_tsvector('english',
        'Answers Answer Response' || ' ' ||
        COALESCE(a."Answer", '') || ' ' ||
        COALESCE(a."More_Information", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(ja."Legal_Families", '') || ' ' ||
        COALESCE(qa."Questions", '') || ' ' ||
        COALESCE(ta."Themes", '') || ' ' ||
        COALESCE((COALESCE(ja."Alpha_3_Code",'') || '_' || COALESCE(qa."CoLD_ID",'')), '')
    ) AS document
FROM {S}."Answers" a
LEFT JOIN jurisdiction_agg ja ON ja."Answers_id" = a.id
LEFT JOIN questions_agg qa ON qa."Answers_id" = a.id
LEFT JOIN themes_agg ta ON ta."Answers_id" = a.id;
"""


ANSWERS_MV_ORIGINAL = f"""
DROP MATERIALIZED VIEW IF EXISTS data_views.answers CASCADE;
CREATE MATERIALIZED VIEW data_views.answers AS
WITH jurisdiction_agg AS (
    SELECT
        m2m."Answers_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions",
        STRING_AGG(j."Legal_Family", ' | ' ORDER BY j."Legal_Family") AS "Legal_Families",
        MIN(j."Alpha_3_Code") AS "Alpha_3_Code"
    FROM {S}."_nc_m2m_Jurisdictions_Answers" m2m
    JOIN {S}."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Answers_id"
),
questions_agg AS (
    SELECT
        m2m."Answers_id",
        STRING_AGG(q."Question", ' | ' ORDER BY q.id) AS "Questions",
        STRING_AGG(DISTINCT t."Theme", ' | ' ORDER BY t."Theme") AS "Themes",
        MIN(q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM {S}."_nc_m2m_Questions_Answers" m2m
    JOIN {S}."Questions" q ON q.id = m2m."Questions_id"
    LEFT JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = q.id
    LEFT JOIN {S}."Themes" t ON t.id = tq."Themes_id"
    GROUP BY m2m."Answers_id"
)
SELECT
    a.id,
    a."Answer",
    a."More_Information",
    'Answers Answer Response' AS "Table_Synonyms",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(ja."Legal_Families", '') AS "Legal_Families",
    COALESCE(qa."Questions", '') AS "Questions",
    COALESCE(qa."Themes", '') AS "Themes",
    (COALESCE(ja."Alpha_3_Code",'') || '_' || COALESCE(qa."CoLD_ID",'')) AS "CoLD_ID",
    a."updated_at"::date AS sort_date,
    to_tsvector('english',
        'Answers Answer Response' || ' ' ||
        COALESCE(a."Answer", '') || ' ' ||
        COALESCE(a."More_Information", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(ja."Legal_Families", '') || ' ' ||
        COALESCE(qa."Questions", '') || ' ' ||
        COALESCE(qa."Themes", '') || ' ' ||
        COALESCE((COALESCE(ja."Alpha_3_Code",'') || '_' || COALESCE(qa."CoLD_ID",'')), '')
    ) AS document
FROM {S}."Answers" a
LEFT JOIN jurisdiction_agg ja ON ja."Answers_id" = a.id
LEFT JOIN questions_agg qa ON qa."Answers_id" = a.id;
"""


ANSWERS_MV_INDEXES = """
CREATE INDEX idx_fts_answers ON data_views.answers USING GIN(document);
CREATE UNIQUE INDEX idx_answers_id ON data_views.answers(id);
"""


def upgrade() -> None:
    op.execute(ANSWERS_MV_FIXED)
    op.execute(ANSWERS_MV_INDEXES)


def downgrade() -> None:
    op.execute(ANSWERS_MV_ORIGINAL)
    op.execute(ANSWERS_MV_INDEXES)
