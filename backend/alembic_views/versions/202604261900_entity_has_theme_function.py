"""Centralize theme-filter join chains in ``data_views.entity_has_theme``.

Theme filtering used to live in three places:
  - the materialized-view ``themes_agg`` CTEs,
  - ``data_views.get_entity_detail`` (themes relations), and
  - hand-built EXISTS clauses inside ``backend/app/services/entity_list.py``.

The Python side knew NocoDB table names directly, so when revision
``202604261800`` switched Court Decisions to derive themes through the answer
chain, the entity-list filter silently kept hitting the now-deprecated direct
M2M table and returned 0 rows.

This migration introduces a single SQL dispatcher that all callers ask the
same question::

    SELECT data_views.entity_has_theme('court-decisions', cd_id, 'Public policy');

Handled slugs (kebab-case, mirroring ``EntityListConfig.slug``):
  - ``court-decisions``  → Court_Decisions ← Answers ← Questions ← Themes
  - ``literature``       → Literature ← Themes (direct)
  - ``arbitral-awards``  → Arbitral_Awards ← Themes (direct)

Any other slug returns FALSE so callers that pass arbitrary slugs degrade to
"no rows" rather than erroring out.
"""

from __future__ import annotations

from alembic import op

revision = "202604261900"
down_revision = "202604261800"
branch_labels = None
depends_on = None

SCHEMA = "p1q5x3pj29vkrdr"

ENTITY_HAS_THEME = f"""
CREATE OR REPLACE FUNCTION data_views.entity_has_theme(
    p_slug TEXT,
    p_entity_id INT,
    p_theme TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    IF p_slug = 'court-decisions' THEN
        RETURN EXISTS (
            SELECT 1
            FROM "{SCHEMA}"."_nc_m2m_Answers_Court_Decisions" acd
            JOIN "{SCHEMA}"."_nc_m2m_Questions_Answers" qa ON qa."Answers_id" = acd."Answers_id"
            JOIN "{SCHEMA}"."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = qa."Questions_id"
            JOIN "{SCHEMA}"."Themes" t ON t.id = tq."Themes_id"
            WHERE acd."Court_Decisions_id" = p_entity_id
              AND t."Theme" = p_theme
        );
    ELSIF p_slug = 'literature' THEN
        RETURN EXISTS (
            SELECT 1
            FROM "{SCHEMA}"."_nc_m2m_Themes_Literature" m
            JOIN "{SCHEMA}"."Themes" t ON t.id = m."Themes_id"
            WHERE m."Literature_id" = p_entity_id
              AND t."Theme" = p_theme
        );
    ELSIF p_slug = 'arbitral-awards' THEN
        RETURN EXISTS (
            SELECT 1
            FROM "{SCHEMA}"."_nc_m2m_Themes_Arbitral_Awards" m
            JOIN "{SCHEMA}"."Themes" t ON t.id = m."Themes_id"
            WHERE m."Arbitral_Awards_id" = p_entity_id
              AND t."Theme" = p_theme
        );
    END IF;
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE;
"""


DROP_ENTITY_HAS_THEME = """
DROP FUNCTION IF EXISTS data_views.entity_has_theme(TEXT, INT, TEXT);
"""


def upgrade() -> None:
    op.execute(ENTITY_HAS_THEME)


def downgrade() -> None:
    op.execute(DROP_ENTITY_HAS_THEME)
