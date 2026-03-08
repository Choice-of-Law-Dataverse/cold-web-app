from __future__ import annotations

from alembic import op

revision = "202603081200"
down_revision = "202603081100"
branch_labels = None
depends_on = None

SCHEMA = "p1q5x3pj29vkrdr"

ARBITRAL_AWARDS_FTS = f"""
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_awards CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_awards AS
WITH jurisdiction_agg AS (
    SELECT
        m2m."Arbitral_Awards_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions"
    FROM {SCHEMA}."_nc_m2m_Jurisdictions_Arbitral_Awards" m2m
    JOIN {SCHEMA}."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Arbitral_Awards_id"
),
themes_agg AS (
    SELECT
        m2m."Arbitral_Awards_id",
        STRING_AGG(t."Theme", ' | ' ORDER BY t."Theme") AS "Themes"
    FROM {SCHEMA}."_nc_m2m_Themes_Arbitral_Awards" m2m
    JOIN {SCHEMA}."Themes" t ON t.id = m2m."Themes_id"
    GROUP BY m2m."Arbitral_Awards_id"
),
institutions_agg AS (
    SELECT
        m2m."Arbitral_Awards_id",
        STRING_AGG(ai."Institution", ' | ' ORDER BY ai."Institution") AS "Institutions"
    FROM {SCHEMA}."_nc_m2m_Arbitral_Instit_Arbitral_Awards" m2m
    JOIN {SCHEMA}."Arbitral_Institutions" ai ON ai.id = m2m."Arbitral_Institutions_id"
    GROUP BY m2m."Arbitral_Awards_id"
)
SELECT
    aa.id,
    aa."Case_Number",
    aa."Context",
    aa."Award_Summary",
    aa."Year",
    aa."Nature_of_the_Award",
    aa."Seat__Town_",
    aa."Source",
    'Arbitral Awards Arbitration Award' AS "Table_Synonyms",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(ta."Themes", '') AS "Themes",
    ('AA-' || aa."ID_Number") AS "CoLD_ID",
    CASE
      WHEN aa."Year"::text ~ '^[0-9]{{4}}$'
        THEN to_date(aa."Year"::text, 'YYYY')
      ELSE NULL
    END AS sort_date,
    to_tsvector('english',
        'Arbitral Awards Arbitration Award' || ' ' ||
        COALESCE(aa."Case_Number", '') || ' ' ||
        COALESCE(aa."Context", '') || ' ' ||
        COALESCE(aa."Award_Summary", '') || ' ' ||
        COALESCE(aa."Year"::text, '') || ' ' ||
        COALESCE(aa."Nature_of_the_Award", '') || ' ' ||
        COALESCE(aa."Seat__Town_", '') || ' ' ||
        COALESCE(ia."Institutions", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(ta."Themes", '') || ' ' ||
        ('AA-' || aa."ID_Number")
    ) AS document
FROM {SCHEMA}."Arbitral_Awards" aa
LEFT JOIN jurisdiction_agg ja ON ja."Arbitral_Awards_id" = aa.id
LEFT JOIN themes_agg ta ON ta."Arbitral_Awards_id" = aa.id
LEFT JOIN institutions_agg ia ON ia."Arbitral_Awards_id" = aa.id;
"""

ARBITRAL_RULES_FTS = f"""
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_rules CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_rules AS
WITH institutions_agg AS (
    SELECT
        m2m."Arbitral_Rules_id",
        STRING_AGG(ai."Institution", ' | ' ORDER BY ai."Institution") AS "Institutions"
    FROM {SCHEMA}."_nc_m2m_Arbitral_Instit_Arbitral_Rules" m2m
    JOIN {SCHEMA}."Arbitral_Institutions" ai ON ai.id = m2m."Arbitral_Institutions_id"
    GROUP BY m2m."Arbitral_Rules_id"
)
SELECT
    ar.id,
    ar."Set_of_Rules",
    ar."In_Force_From",
    'Arbitral Rules Arbitration Rules Procedure' AS "Table_Synonyms",
    COALESCE(ia."Institutions", '') AS "Institutions",
    ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS "CoLD_ID",
    ar."In_Force_From" AS sort_date,
    to_tsvector('english',
        'Arbitral Rules Arbitration Rules Procedure' || ' ' ||
        COALESCE(ar."Set_of_Rules", '') || ' ' ||
        COALESCE(ar."In_Force_From"::text, '') || ' ' ||
        COALESCE(ia."Institutions", '') || ' ' ||
        ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text))
    ) AS document
FROM {SCHEMA}."Arbitral_Rules" ar
LEFT JOIN institutions_agg ia ON ia."Arbitral_Rules_id" = ar.id;
"""

SEARCH_ALL_V4 = f"""
DROP FUNCTION IF EXISTS data_views.search_all_v2(text, text[], text[], text[], integer, integer, boolean);

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
              FROM {SCHEMA}."_nc_m2m_Jurisdictions_Answers" ja
              JOIN {SCHEMA}."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
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

        UNION ALL

        SELECT
            'Arbitral Awards'::text AS table_name,
            aa.id AS record_id,
            to_jsonb(aa.*) || jsonb_build_object(
                'jurisdictions', sv."Jurisdictions",
                'themes', sv."Themes"
            ) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_arbitral_awards aa
        JOIN data_views.arbitral_awards sv ON sv.id = aa.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Arbitral Awards' = ANY(filter_tables))
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
            'Arbitral Rules'::text AS table_name,
            ar.id AS record_id,
            to_jsonb(ar.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0
                 ELSE ts_rank(sv.document, plainto_tsquery('english', search_term))
            END AS rank,
            sv.sort_date AS result_date
        FROM data_views.base_arbitral_rules ar
        JOIN data_views.arbitral_rules sv ON sv.id = ar.id
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Arbitral Rules' = ANY(filter_tables))

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

SEARCH_ALL_COUNT_V4 = f"""
DROP FUNCTION IF EXISTS data_views.search_all_count_v2(text, text[], text[], text[]);

CREATE OR REPLACE FUNCTION data_views.search_all_count_v2(
    search_term TEXT,
    filter_tables TEXT[] DEFAULT NULL,
    filter_jurisdictions TEXT[] DEFAULT NULL,
    filter_themes TEXT[] DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    empty_term BOOLEAN := (search_term IS NULL OR btrim(search_term) = '');
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total
    FROM (
        SELECT 1
        FROM data_views.answers sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Answers' = ANY(filter_tables))
          AND NOT EXISTS (
              SELECT 1
              FROM {SCHEMA}."_nc_m2m_Jurisdictions_Answers" ja
              JOIN {SCHEMA}."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
              WHERE ja."Answers_id" = sv.id
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

        SELECT 1
        FROM data_views.hcch_answers sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'HCCH Answers' = ANY(filter_tables))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT 1
        FROM data_views.court_decisions sv
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

        SELECT 1
        FROM data_views.domestic_instruments sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Domestic Instruments' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))

        UNION ALL

        SELECT 1
        FROM data_views.regional_instruments sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Regional Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT 1
        FROM data_views.international_instruments sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'International Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT 1
        FROM data_views.literature sv
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

        UNION ALL

        SELECT 1
        FROM data_views.arbitral_awards sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Arbitral Awards' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE sv."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE sv."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT 1
        FROM data_views.arbitral_rules sv
        WHERE (empty_term OR sv.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Arbitral Rules' = ANY(filter_tables))
    ) AS sub;

    RETURN total;
END;
$$ LANGUAGE plpgsql STABLE;
"""


def upgrade() -> None:
    op.execute(ARBITRAL_AWARDS_FTS)
    op.execute("CREATE INDEX idx_fts_arbitral_awards ON data_views.arbitral_awards USING GIN(document)")
    op.execute("CREATE UNIQUE INDEX idx_arbitral_awards_id ON data_views.arbitral_awards(id)")

    op.execute(ARBITRAL_RULES_FTS)
    op.execute("CREATE INDEX idx_fts_arbitral_rules ON data_views.arbitral_rules USING GIN(document)")
    op.execute("CREATE UNIQUE INDEX idx_arbitral_rules_id ON data_views.arbitral_rules(id)")

    op.execute(SEARCH_ALL_V4)
    op.execute(SEARCH_ALL_COUNT_V4)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_awards CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_rules CASCADE")
