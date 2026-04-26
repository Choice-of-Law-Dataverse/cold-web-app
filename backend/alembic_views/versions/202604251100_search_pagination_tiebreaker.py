from __future__ import annotations

from alembic import op

revision = "202604251100"
down_revision = "202604251000"
branch_labels = None
depends_on = None


SEARCH_ALL_V3_WITH_TIEBREAKER = """
CREATE OR REPLACE FUNCTION data_views.search_all_v2(
    search_term TEXT,
    filter_tables TEXT[] DEFAULT NULL,
    filter_jurisdictions TEXT[] DEFAULT NULL,
    filter_themes TEXT[] DEFAULT NULL,
    page INT DEFAULT 1,
    page_size INT DEFAULT 50,
    sort_by_date BOOLEAN DEFAULT FALSE
)
RETURNS TABLE(
    table_name TEXT,
    record_id INTEGER,
    complete_record JSONB,
    rank REAL,
    result_date DATE
) AS $$
DECLARE
    empty_term BOOLEAN := (search_term IS NULL OR btrim(search_term) = '');
    offset_val INT := (page - 1) * page_size;
BEGIN
    RETURN QUERY
    SELECT sub.*
    FROM (
        SELECT
            'Answers'::text AS table_name,
            a.id AS record_id,
            to_jsonb(a.*) || jsonb_build_object(
                'question', sv."Questions",
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_answers a
        JOIN data_views.answers sv ON sv.id = a.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Answers' = ANY(filter_tables))
          AND NOT EXISTS (
              SELECT 1
              FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
              JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
              WHERE ja."Answers_id" = a.id
                AND COALESCE(j."Irrelevant_", FALSE) = TRUE
          )
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'HCCH Answers'::text AS table_name,
            ha.id AS record_id,
            to_jsonb(ha.*) || jsonb_build_object(
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_hcch_answers ha
        JOIN data_views.hcch_answers sv ON sv.id = ha.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'HCCH Answers' = ANY(filter_tables))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'Court Decisions'::text AS table_name,
            cd.id AS record_id,
            to_jsonb(cd.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_court_decisions cd
        JOIN data_views.court_decisions sv ON sv.id = cd.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Court Decisions' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'Domestic Instruments'::text AS table_name,
            di.id AS record_id,
            to_jsonb(di.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_domestic_instruments di
        JOIN data_views.domestic_instruments sv ON sv.id = di.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Domestic Instruments' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))

        UNION ALL

        SELECT
            'Regional Instruments'::text AS table_name,
            ri.id AS record_id,
            to_jsonb(ri.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_regional_instruments ri
        JOIN data_views.regional_instruments sv ON sv.id = ri.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Regional Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT
            'International Instruments'::text AS table_name,
            ii.id AS record_id,
            to_jsonb(ii.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_international_instruments ii
        JOIN data_views.international_instruments sv ON sv.id = ii.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'International Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT
            'Literature'::text AS table_name,
            l.id AS record_id,
            to_jsonb(l.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_literature l
        JOIN data_views.literature sv ON sv.id = l.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Literature' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

    ) AS sub
    ORDER BY
        CASE
            WHEN sub.table_name = 'Answers'
                 AND btrim(COALESCE(sub.complete_record->>'answer', '')) ILIKE '%no data%'
            THEN 2
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'case_rank')::numeric, 1000000) <= 5
            THEN 1
            ELSE 0
        END ASC,
        CASE
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'case_rank')::numeric, 1000000) <= 5
            THEN COALESCE((sub.complete_record->>'case_rank')::numeric, -1)
        END DESC NULLS LAST,
        CASE WHEN sort_by_date THEN sub.result_date ELSE NULL END DESC NULLS LAST,
        sub.rank DESC,
        sub.table_name,
        sub.record_id ASC
    LIMIT page_size OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
"""


SEARCH_ALL_V3_WITHOUT_TIEBREAKER = """
CREATE OR REPLACE FUNCTION data_views.search_all_v2(
    search_term TEXT,
    filter_tables TEXT[] DEFAULT NULL,
    filter_jurisdictions TEXT[] DEFAULT NULL,
    filter_themes TEXT[] DEFAULT NULL,
    page INT DEFAULT 1,
    page_size INT DEFAULT 50,
    sort_by_date BOOLEAN DEFAULT FALSE
)
RETURNS TABLE(
    table_name TEXT,
    record_id INTEGER,
    complete_record JSONB,
    rank REAL,
    result_date DATE
) AS $$
DECLARE
    empty_term BOOLEAN := (search_term IS NULL OR btrim(search_term) = '');
    offset_val INT := (page - 1) * page_size;
BEGIN
    RETURN QUERY
    SELECT sub.*
    FROM (
        SELECT
            'Answers'::text AS table_name,
            a.id AS record_id,
            to_jsonb(a.*) || jsonb_build_object(
                'question', sv."Questions",
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_answers a
        JOIN data_views.answers sv ON sv.id = a.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Answers' = ANY(filter_tables))
          AND NOT EXISTS (
              SELECT 1
              FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
              JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
              WHERE ja."Answers_id" = a.id
                AND COALESCE(j."Irrelevant_", FALSE) = TRUE
          )
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'HCCH Answers'::text AS table_name,
            ha.id AS record_id,
            to_jsonb(ha.*) || jsonb_build_object(
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_hcch_answers ha
        JOIN data_views.hcch_answers sv ON sv.id = ha.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'HCCH Answers' = ANY(filter_tables))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'Court Decisions'::text AS table_name,
            cd.id AS record_id,
            to_jsonb(cd.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_court_decisions cd
        JOIN data_views.court_decisions sv ON sv.id = cd.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Court Decisions' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT
            'Domestic Instruments'::text AS table_name,
            di.id AS record_id,
            to_jsonb(di.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_domestic_instruments di
        JOIN data_views.domestic_instruments sv ON sv.id = di.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Domestic Instruments' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))

        UNION ALL

        SELECT
            'Regional Instruments'::text AS table_name,
            ri.id AS record_id,
            to_jsonb(ri.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_regional_instruments ri
        JOIN data_views.regional_instruments sv ON sv.id = ri.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Regional Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT
            'International Instruments'::text AS table_name,
            ii.id AS record_id,
            to_jsonb(ii.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_international_instruments ii
        JOIN data_views.international_instruments sv ON sv.id = ii.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'International Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT
            'Literature'::text AS table_name,
            l.id AS record_id,
            to_jsonb(l.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_literature l
        JOIN data_views.literature sv ON sv.id = l.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Literature' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

    ) AS sub
    ORDER BY
        CASE
            WHEN sub.table_name = 'Answers'
                 AND btrim(COALESCE(sub.complete_record->>'answer', '')) ILIKE '%no data%'
            THEN 2
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'case_rank')::numeric, 1000000) <= 5
            THEN 1
            ELSE 0
        END ASC,
        CASE
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'case_rank')::numeric, 1000000) <= 5
            THEN COALESCE((sub.complete_record->>'case_rank')::numeric, -1)
        END DESC NULLS LAST,
        CASE WHEN sort_by_date THEN sub.result_date ELSE NULL END DESC NULLS LAST,
        sub.rank DESC,
        sub.table_name
    LIMIT page_size OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(SEARCH_ALL_V3_WITH_TIEBREAKER)


def downgrade() -> None:
    op.execute(SEARCH_ALL_V3_WITHOUT_TIEBREAKER)
