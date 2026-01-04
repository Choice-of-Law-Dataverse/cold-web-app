-- Create schema for the comprehensive materialized views (if it doesn't exist)
CREATE SCHEMA IF NOT EXISTS data_views;

-- Function to refresh all materialized views in the data_views schema
CREATE OR REPLACE FUNCTION data_views.refresh_all_materialized_views()
RETURNS void AS $$
DECLARE
    view_name TEXT;
    has_unique_index BOOLEAN;
BEGIN
    FOR view_name IN 
        SELECT matviewname FROM pg_matviews WHERE schemaname = 'data_views'
    LOOP
        -- Check if the materialized view has a unique index
        SELECT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE schemaname = 'data_views' 
            AND tablename = view_name
            AND indexdef LIKE '%UNIQUE%'
        ) INTO has_unique_index;
        
        IF has_unique_index THEN
            -- If it has a unique index, refresh concurrently
            EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY data_views.%I', view_name);
        ELSE
            -- If it doesn't have a unique index, refresh non-concurrently
            EXECUTE format('REFRESH MATERIALIZED VIEW data_views.%I', view_name);
            RAISE NOTICE 'Materialized view data_views.% refreshed non-concurrently (no unique index)', view_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- COMPREHENSIVE MATERIALIZED VIEWS
-- =====================================

-- 1. Questions: (({Question Number} & "-") & {Primary Theme})
DROP MATERIALIZED VIEW IF EXISTS data_views.questions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.questions_complete AS
SELECT 
    q.*,
    (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID",
    -- (rest as before...)
    (
        SELECT jsonb_agg(t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_Questions" tq
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tq."Themes_id"
        WHERE tq."Questions_id" = q.id
    ) AS related_themes,
    (
        SELECT jsonb_agg(a.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
        JOIN p1q5x3pj29vkrdr."Answers" a ON a.id = qa."Answers_id"
        WHERE qa."Questions_id" = q.id
    ) AS related_answers,
    (
        SELECT jsonb_agg(cd.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Court_Decisions" qcd
        JOIN p1q5x3pj29vkrdr."Court_Decisions" cd ON cd.id = qcd."Court_Decisions_id"
        WHERE qcd."Questions_id" = q.id
    ) AS related_court_decisions,
    (
        SELECT jsonb_agg(di.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Domestic_Instru" qdi
        JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = qdi."Domestic_Instruments_id"
        WHERE qdi."Questions_id" = q.id
    ) AS related_domestic_instruments
FROM p1q5x3pj29vkrdr."Questions" q;

CREATE UNIQUE INDEX idx_questions_complete_id ON data_views.questions_complete(id);

-- 2. Answers: (({Jurisdictions Alpha-3 code} & "_") & {Question ID})
DROP MATERIALIZED VIEW IF EXISTS data_views.answers_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.answers_complete AS
SELECT 
    a.*,
    -- Get first related Jurisdiction Alpha-3 code
    jcodes."Alpha_3_Code" AS "Jurisdictions_Alpha_3_Code",
    -- Get first related Question's CoLD_ID
    qcold."CoLD_ID" AS "Question_CoLD_ID",
    (COALESCE(jcodes."Alpha_3_Code", '') || '_' || COALESCE(qcold."CoLD_ID", '')) AS "CoLD_ID",
    (
        SELECT jsonb_agg(q.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
        JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qa."Questions_id"
        WHERE qa."Answers_id" = a.id
    ) AS related_questions,
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
        WHERE ja."Answers_id" = a.id
    ) AS related_jurisdictions,
    (
        SELECT jsonb_agg(DISTINCT t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
        JOIN p1q5x3pj29vkrdr."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = qa."Questions_id"
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tq."Themes_id"
        WHERE qa."Answers_id" = a.id
    ) AS related_themes,
    (
        SELECT jsonb_agg(
            to_jsonb(cd) || jsonb_build_object(
                'CoLD_ID', ('CD-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || COALESCE(cd."ID_Number"::text, ''))
            )
        )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Court_Decisions" acd
        JOIN p1q5x3pj29vkrdr."Court_Decisions" cd ON cd.id = acd."Court_Decisions_id"
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" jcd
            JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
            WHERE jcd."Court_Decisions_id" = cd.id
            LIMIT 1
        ) jcodes ON true
        WHERE acd."Answers_id" = a.id
    ) AS related_court_decisions,
    (
        SELECT jsonb_agg(l.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Literature" al
        JOIN p1q5x3pj29vkrdr."Literature" l ON l.id = al."Literature_id"
        WHERE al."Answers_id" = a.id
    ) AS related_literature,
    (
        SELECT jsonb_agg(
            to_jsonb(di) || jsonb_build_object(
                'CoLD_ID', (
                    'DI-' || COALESCE(jdi."Alpha_3_Code", '') || '-' || COALESCE(di."ID_Number"::text, '')
                )
            )
        )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Domestic_Instru" adi
        JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = adi."Domestic_Instruments_id"
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
            JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
            WHERE jdi."Domestic_Instruments_id" = di.id
            LIMIT 1
        ) jdi ON true
        WHERE adi."Answers_id" = a.id
    ) AS related_domestic_instruments,
    (
        SELECT jsonb_agg(
            to_jsonb(dlp) || jsonb_build_object(
                'CoLD_ID', (
                    'DI-' || COALESCE(jdi."Alpha_3_Code", '') || '-' || COALESCE(di."ID_Number"::text, '') || ' ' || COALESCE(dlp."Article", '')
                )
            )
        )
        FROM (
            SELECT dlp.id, dlp."Article", dlp."ncRecordId", dlp."created_at", dlp."updated_at", dlp."created_by", dlp."updated_by"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Domestic_Legal_" adl
            JOIN p1q5x3pj29vkrdr."Domestic_Legal_Provisions" dlp ON dlp.id = adl."Domestic_Legal_Provisions_id"
            WHERE adl."Answers_id" = a.id
            UNION
            SELECT dlp1.id, dlp1."Article", dlp1."ncRecordId", dlp1."created_at", dlp1."updated_at", dlp1."created_by", dlp1."updated_by"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Domestic_Legal_1" adl1
            JOIN p1q5x3pj29vkrdr."Domestic_Legal_Provisions" dlp1 ON dlp1.id = adl1."Domestic_Legal_Provisions_id"
            WHERE adl1."Answers_id" = a.id
        ) dlp
        LEFT JOIN p1q5x3pj29vkrdr."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp ON didlp."Domestic_Legal_Provisions_id" = dlp.id
        LEFT JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = didlp."Domestic_Instruments_id"
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
            JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
            WHERE jdi."Domestic_Instruments_id" = di.id
            LIMIT 1
        ) jdi ON true
    ) AS related_domestic_legal_provisions
FROM p1q5x3pj29vkrdr."Answers" a
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
    WHERE ja."Answers_id" = a.id
    LIMIT 1
) jcodes ON true
LEFT JOIN LATERAL (
    SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qa."Questions_id"
    WHERE qa."Answers_id" = a.id
    LIMIT 1
) qcold ON true;

CREATE UNIQUE INDEX idx_answers_complete_id ON data_views.answers_complete(id);

-- 3. HCCH Answers: ("HCCH-" & {Questions ID}), {Questions ID} is the first related Questions CoLD_ID
DROP MATERIALIZED VIEW IF EXISTS data_views.hcch_answers_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.hcch_answers_complete AS
SELECT 
    ha.*,
    qcold."CoLD_ID" AS "Question_CoLD_ID",
    ('HCCH-' || COALESCE(qcold."CoLD_ID", '')) AS "CoLD_ID",
    (
        SELECT jsonb_agg(t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_HCCH_Answers" tha
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tha."Themes_id"
        WHERE tha."HCCH_Answers_id" = ha.id
    ) AS related_themes,
    (
        SELECT jsonb_agg(ii.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_HCCH_Answers_International_I" haii
        JOIN p1q5x3pj29vkrdr."International_Instruments" ii ON ii.id = haii."International_Instruments_id"
        WHERE haii."HCCH_Answers_id" = ha.id
    ) AS related_international_instruments
FROM p1q5x3pj29vkrdr."HCCH_Answers" ha
LEFT JOIN LATERAL (
    SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qa."Questions_id"
    WHERE qa."Answers_id" = ha.id
    LIMIT 1
) qcold ON true;

CREATE UNIQUE INDEX idx_hcch_answers_complete_id ON data_views.hcch_answers_complete(id);

-- 4. Domestic Instruments: ((("DI-" & {Jurisdictions Alpha-3 Code}) & "-") & {ID Number})
DROP MATERIALIZED VIEW IF EXISTS data_views.domestic_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.domestic_instruments_complete AS
SELECT 
    di.*,
    jcodes."Alpha_3_Code" AS "Jurisdictions_Alpha_3_Code",
    ('DI-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || di."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
        WHERE jdi."Domestic_Instruments_id" = di.id
    ) AS related_jurisdictions,
    (
        SELECT jsonb_agg(
                   to_jsonb(dlp)
                   || jsonb_build_object(
                        'CoLD_ID',
                        ('DI-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || di."ID_Number" || ' ' || dlp."Article")
                   )
               )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp
        JOIN p1q5x3pj29vkrdr."Domestic_Legal_Provisions" dlp ON dlp.id = didlp."Domestic_Legal_Provisions_id"
        WHERE didlp."Domestic_Instruments_id" = di.id
    ) AS related_legal_provisions,
    (
        SELECT jsonb_agg(q.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Domestic_Instru" qdi
        JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qdi."Questions_id"
        WHERE qdi."Domestic_Instruments_id" = di.id
    ) AS related_questions
FROM p1q5x3pj29vkrdr."Domestic_Instruments" di
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
    WHERE jdi."Domestic_Instruments_id" = di.id
    LIMIT 1
) jcodes ON true;

CREATE UNIQUE INDEX idx_domestic_instruments_complete_id ON data_views.domestic_instruments_complete(id);

-- 5. Domestic Legal Provisions: (({Domestic Instruments ID} & " ") & {Article}), {Domestic Instruments ID} is CoLD_ID of the related Domestic Instrument
DROP MATERIALIZED VIEW IF EXISTS data_views.domestic_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.domestic_legal_provisions_complete AS
SELECT 
    dlp.*,
    di_cold."CoLD_ID" AS "Domestic_Instrument_CoLD_ID",
    (COALESCE(di_cold."CoLD_ID", '') || ' ' || dlp."Article") AS "CoLD_ID",
    (
        SELECT jsonb_agg(di.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp
        JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = didlp."Domestic_Instruments_id"
        WHERE didlp."Domestic_Legal_Provisions_id" = dlp.id
    ) AS related_domestic_instruments
FROM p1q5x3pj29vkrdr."Domestic_Legal_Provisions" dlp
LEFT JOIN LATERAL (
    SELECT 
        ('DI-' || COALESCE(j."Alpha_3_Code", '') || '-' || di."ID_Number") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp
    JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = didlp."Domestic_Instruments_id"
    LEFT JOIN p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi ON jdi."Domestic_Instruments_id" = di.id
    LEFT JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
    WHERE didlp."Domestic_Legal_Provisions_id" = dlp.id
    LIMIT 1
) di_cold ON true;

CREATE UNIQUE INDEX idx_domestic_legal_provisions_complete_id ON data_views.domestic_legal_provisions_complete(id);

-- 6. Regional Instruments: ((("RI-" & LEFT({Abbreviation}, 3)) & "-") & {ID Number})
DROP MATERIALIZED VIEW IF EXISTS data_views.regional_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.regional_instruments_complete AS
SELECT 
    ri.*,
    ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(s.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Regional_Instru_Specialists" ris
        JOIN p1q5x3pj29vkrdr."Specialists" s ON s.id = ris."Specialists_id"
        WHERE ris."Regional_Instruments_id" = ri.id
    ) AS related_specialists,
    (
        SELECT jsonb_agg(
                   to_jsonb(rlp)
                   || jsonb_build_object(
                        'CoLD_ID',
                        ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number" || ' ' || rlp."Provision")
                   )
               )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Regional_Instru_Regional_Legal_" mirl
        JOIN p1q5x3pj29vkrdr."Regional_Legal_Provisions" rlp ON rlp.id = mirl."Regional_Legal_Provisions_id"
        WHERE mirl."Regional_Instruments_id" = ri.id
    ) AS related_legal_provisions
FROM p1q5x3pj29vkrdr."Regional_Instruments" ri;

CREATE UNIQUE INDEX idx_regional_instruments_complete_id ON data_views.regional_instruments_complete(id);

-- 7. Regional Legal Provisions: (({Instrument} & " ") & {Provision}), Instrument is Regional Instruments CoLD_ID
DROP MATERIALIZED VIEW IF EXISTS data_views.regional_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.regional_legal_provisions_complete AS
SELECT 
    rlp.*,
    ri_cold."CoLD_ID" AS "Instrument_CoLD_ID",
    (COALESCE(ri_cold."CoLD_ID", '') || ' ' || rlp."Provision") AS "CoLD_ID",
    (
        SELECT jsonb_agg(ri.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Regional_Instru_Regional_Legal_" mirl2
        JOIN p1q5x3pj29vkrdr."Regional_Instruments" ri ON ri.id = mirl2."Regional_Instruments_id"
        WHERE mirl2."Regional_Legal_Provisions_id" = rlp.id
    ) AS related_regional_instruments
FROM p1q5x3pj29vkrdr."Regional_Legal_Provisions" rlp
LEFT JOIN LATERAL (
    SELECT ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Regional_Instru_Regional_Legal_" mirl
    JOIN p1q5x3pj29vkrdr."Regional_Instruments" ri ON ri.id = mirl."Regional_Instruments_id"
    WHERE mirl."Regional_Legal_Provisions_id" = rlp.id
    LIMIT 1
) ri_cold ON true;

CREATE UNIQUE INDEX idx_regional_legal_provisions_complete_id ON data_views.regional_legal_provisions_complete(id);

-- 8. International Instruments: ((("II-" & LEFT({Name}, 3)) & "-") & {ID Number})
DROP MATERIALIZED VIEW IF EXISTS data_views.international_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.international_instruments_complete AS
SELECT 
    ii.*,
    ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(s.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_Specialists" iis
        JOIN p1q5x3pj29vkrdr."Specialists" s ON s.id = iis."Specialists_id"
        WHERE iis."International_Instruments_id" = ii.id
    ) AS related_specialists,
    (
        SELECT jsonb_agg(ha.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_HCCH_Answers_International_I" haii
        JOIN p1q5x3pj29vkrdr."HCCH_Answers" ha ON ha.id = haii."HCCH_Answers_id"
        WHERE haii."International_Instruments_id" = ii.id
    ) AS related_hcch_answers,
    (
        SELECT jsonb_agg(
                   to_jsonb(ilp)
                   || jsonb_build_object(
                        'CoLD_ID',
                        ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number" || ' ' || ilp."Provision")
                   )
               )
        FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_International_L" miil
        JOIN p1q5x3pj29vkrdr."International_Legal_Provisions" ilp ON ilp.id = miil."International_Legal_Provisions_id"
        WHERE miil."International_Instruments_id" = ii.id
    ) AS related_legal_provisions,
    (
        SELECT jsonb_agg(
                   to_jsonb(l)
                   || jsonb_build_object(
                        'CoLD_ID',
                        ('L-' || l."ID_Number")
                   )
               )
        FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_Literature" mil
        JOIN p1q5x3pj29vkrdr."Literature" l ON l.id = mil."Literature_id"
        WHERE mil."International_Instruments_id" = ii.id
    ) AS related_literature
FROM p1q5x3pj29vkrdr."International_Instruments" ii;

CREATE UNIQUE INDEX idx_international_instruments_complete_id ON data_views.international_instruments_complete(id);

-- 9. International Legal Provisions: (({Instrument ID} & " ") & {Provision}), Instrument ID is International Instruments CoLD_ID
DROP MATERIALIZED VIEW IF EXISTS data_views.international_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.international_legal_provisions_complete AS
SELECT 
    ilp.*,
    ii_cold."CoLD_ID" AS "Instrument_CoLD_ID",
    (COALESCE(ii_cold."CoLD_ID", '') || ' ' || ilp."Provision") AS "CoLD_ID"
FROM p1q5x3pj29vkrdr."International_Legal_Provisions" ilp
LEFT JOIN LATERAL (
    SELECT ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_International_L" miil
    JOIN p1q5x3pj29vkrdr."International_Instruments" ii ON ii.id = miil."International_Instruments_id"
    WHERE miil."International_Legal_Provisions_id" = ilp.id
    LIMIT 1
) ii_cold ON true;

CREATE UNIQUE INDEX idx_international_legal_provisions_complete_id ON data_views.international_legal_provisions_complete(id);

-- 10. Court Decisions: ((("CD-" & {Jurisdictions Alpha-3 Code}) & "-") & {ID Number})
DROP MATERIALIZED VIEW IF EXISTS data_views.court_decisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.court_decisions_complete AS
SELECT 
    cd.*,
    jcodes."Alpha_3_Code" AS "Jurisdictions_Alpha_3_Code",
    ('CD-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || cd."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" jcd
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
        WHERE jcd."Court_Decisions_id" = cd.id
    ) AS related_jurisdictions,
    (
        SELECT jsonb_agg(
                   to_jsonb(q)
                   || jsonb_build_object(
                        'CoLD_ID', (q."Question_Number" || '-' || q."Primary_Theme")
                   )
               )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Court_Decisions" qcd
        JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qcd."Questions_id"
        WHERE qcd."Court_Decisions_id" = cd.id
    ) AS related_questions,
    (
        SELECT jsonb_agg(a.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Court_Decisions" acd
        JOIN p1q5x3pj29vkrdr."Answers" a ON a.id = acd."Answers_id"
        WHERE acd."Court_Decisions_id" = cd.id
    ) AS related_answers,
    (
        SELECT jsonb_agg(DISTINCT t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Court_Decisions" qcd
        JOIN p1q5x3pj29vkrdr."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = qcd."Questions_id"
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tq."Themes_id"
        WHERE qcd."Court_Decisions_id" = cd.id
    ) AS related_themes
FROM p1q5x3pj29vkrdr."Court_Decisions" cd
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" jcd
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
    WHERE jcd."Court_Decisions_id" = cd.id
    LIMIT 1
) jcodes ON true;

CREATE UNIQUE INDEX idx_court_decisions_complete_id ON data_views.court_decisions_complete(id);

-- 11. Literature: ("L-" & {ID Number})
DROP MATERIALIZED VIEW IF EXISTS data_views.literature_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.literature_complete AS
SELECT 
    l.*,
    ('L-' || l."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Literature" jl
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jl."Jurisdictions_id"
        WHERE jl."Literature_id" = l.id
    ) AS related_jurisdictions,
    (
        SELECT jsonb_agg(t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_Literature" tl
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tl."Themes_id"
        WHERE tl."Literature_id" = l.id
    ) AS related_themes
FROM p1q5x3pj29vkrdr."Literature" l;

CREATE UNIQUE INDEX idx_literature_complete_id ON data_views.literature_complete(id);

-- 12. Arbitral Awards: ("AA-" & {ID Number}) with full relations
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_awards_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_awards_complete AS
SELECT 
    aa.*, 
    ('AA-' || aa."ID_Number") AS "CoLD_ID",
    (
        SELECT jsonb_agg(ai.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral_Instit_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Institutions" ai ON ai.id = m."Arbitral_Institutions_id"
        WHERE m."Arbitral_Awards_id" = aa.id
    ) AS related_arbitral_institutions,
    (
        SELECT jsonb_agg(ap.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Arbitral Provisions" ap ON ap.id = m."Arbitral Provisions_id"
        WHERE m."Arbitral_Awards_id" = aa.id
    ) AS related_arbitral_provisions,
    (
        SELECT jsonb_agg(cd.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Court_Decisions_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Court_Decisions" cd ON cd.id = m."Court_Decisions_id"
        WHERE m."Arbitral_Awards_id" = aa.id
    ) AS related_court_decisions,
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m."Jurisdictions_id"
        WHERE m."Arbitral_Awards_id" = aa.id
    ) AS related_jurisdictions,
    (
        SELECT jsonb_agg(t.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = m."Themes_id"
        WHERE m."Arbitral_Awards_id" = aa.id
    ) AS related_themes
FROM p1q5x3pj29vkrdr."Arbitral_Awards" aa;

CREATE UNIQUE INDEX idx_arbitral_awards_complete_id ON data_views.arbitral_awards_complete(id);

-- 12b. Arbitral Institutions complete view with relations
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_institutions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_institutions_complete AS
SELECT
    ai.*,
    (
        SELECT jsonb_agg(aa.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral_Instit_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Awards" aa ON aa.id = m."Arbitral_Awards_id"
        WHERE m."Arbitral_Institutions_id" = ai.id
    ) AS related_arbitral_awards,
    (
        SELECT jsonb_agg(ar.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral_Instit_Arbitral_Rules" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Rules" ar ON ar.id = m."Arbitral_Rules_id"
        WHERE m."Arbitral_Institutions_id" = ai.id
    ) AS related_arbitral_rules,
    (
        SELECT jsonb_agg(ap.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Instit" m
        JOIN p1q5x3pj29vkrdr."Arbitral Provisions" ap ON ap.id = m."Arbitral Provisions_id"
        WHERE m."Arbitral_Institutions_id" = ai.id
    ) AS related_arbitral_provisions,
    (
        SELECT jsonb_agg(j.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Arbitral_Instit" m
        JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m."Jurisdictions_id"
        WHERE m."Arbitral_Institutions_id" = ai.id
    ) AS related_jurisdictions
FROM p1q5x3pj29vkrdr."Arbitral_Institutions" ai;

CREATE UNIQUE INDEX idx_arbitral_institutions_complete_id ON data_views.arbitral_institutions_complete(id);

-- 12c. Arbitral Rules complete view with relations
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_rules_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_rules_complete AS
SELECT
    ar.*,
    ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS "CoLD_ID",
    (
        SELECT jsonb_agg(ai.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral_Instit_Arbitral_Rules" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Institutions" ai ON ai.id = m."Arbitral_Institutions_id"
        WHERE m."Arbitral_Rules_id" = ar.id
    ) AS related_arbitral_institutions,
    (
        SELECT jsonb_agg(ap.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Rules" m
        JOIN p1q5x3pj29vkrdr."Arbitral Provisions" ap ON ap.id = m."Arbitral Provisions_id"
        WHERE m."Arbitral_Rules_id" = ar.id
        ) AS related_arbitral_provisions,
        (
                SELECT jsonb_agg(DISTINCT to_jsonb(j))
                FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral_Instit_Arbitral_Rules" air
                JOIN p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Arbitral_Instit" jai
                    ON jai."Arbitral_Institutions_id" = air."Arbitral_Institutions_id"
                JOIN p1q5x3pj29vkrdr."Jurisdictions" j
                    ON j.id = jai."Jurisdictions_id"
                WHERE air."Arbitral_Rules_id" = ar.id
        ) AS related_jurisdictions
FROM p1q5x3pj29vkrdr."Arbitral_Rules" ar;

CREATE UNIQUE INDEX idx_arbitral_rules_complete_id ON data_views.arbitral_rules_complete(id);

-- 12d. Arbitral Provisions complete view with relations
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_provisions_complete AS
SELECT
    ap.*,
    ar_cold."CoLD_ID" AS "Arbitral_Rules_CoLD_ID",
    (COALESCE(ar_cold."CoLD_ID", '') || ' ' || COALESCE(ap."Article", '')) AS "CoLD_ID",
    (
        SELECT jsonb_agg(aa.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Awards" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Awards" aa ON aa.id = m."Arbitral_Awards_id"
        WHERE m."Arbitral Provisions_id" = ap.id
    ) AS related_arbitral_awards,
    (
        SELECT jsonb_agg(ai.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Instit" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Institutions" ai ON ai.id = m."Arbitral_Institutions_id"
        WHERE m."Arbitral Provisions_id" = ap.id
    ) AS related_arbitral_institutions,
    (
        SELECT jsonb_agg(ar.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Rules" m
        JOIN p1q5x3pj29vkrdr."Arbitral_Rules" ar ON ar.id = m."Arbitral_Rules_id"
        WHERE m."Arbitral Provisions_id" = ap.id
    ) AS related_arbitral_rules
FROM p1q5x3pj29vkrdr."Arbitral Provisions" ap
LEFT JOIN LATERAL (
    SELECT ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Arbitral Provis_Arbitral_Rules" m
    JOIN p1q5x3pj29vkrdr."Arbitral_Rules" ar ON ar.id = m."Arbitral_Rules_id"
    WHERE m."Arbitral Provisions_id" = ap.id
    LIMIT 1
) ar_cold ON true;

CREATE UNIQUE INDEX idx_arbitral_provisions_complete_id ON data_views.arbitral_provisions_complete(id);

-- 13. Jurisdictions: CoLD_ID is Alpha-3 code, include direct relations to other entities
DROP MATERIALIZED VIEW IF EXISTS data_views.jurisdictions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.jurisdictions_complete AS
SELECT
    j.*,
    j."Alpha_3_Code" AS "CoLD_ID",
    (
        SELECT jsonb_agg(a.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
        JOIN p1q5x3pj29vkrdr."Answers" a ON a.id = ja."Answers_id"
        WHERE ja."Jurisdictions_id" = j.id
    ) AS related_answers,
    (
        SELECT jsonb_agg(di.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
        JOIN p1q5x3pj29vkrdr."Domestic_Instruments" di ON di.id = jdi."Domestic_Instruments_id"
        WHERE jdi."Jurisdictions_id" = j.id
    ) AS related_domestic_instruments,
    (
        SELECT jsonb_agg(cd.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" jcd
        JOIN p1q5x3pj29vkrdr."Court_Decisions" cd ON cd.id = jcd."Court_Decisions_id"
        WHERE jcd."Jurisdictions_id" = j.id
    ) AS related_court_decisions,
    (
        SELECT jsonb_agg(l.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Literature" jl
        JOIN p1q5x3pj29vkrdr."Literature" l ON l.id = jl."Literature_id"
        WHERE jl."Jurisdictions_id" = j.id
    ) AS related_literature,
    (
        SELECT jsonb_agg(s.*)
        FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Specialists" js
        JOIN p1q5x3pj29vkrdr."Specialists" s ON s.id = js."Specialists_id"
        WHERE js."Jurisdictions_id" = j.id
    ) AS related_specialists
FROM p1q5x3pj29vkrdr."Jurisdictions" j;
CREATE UNIQUE INDEX idx_jurisdictions_complete_id ON data_views.jurisdictions_complete(id);


-- =====================================
-- SEARCH-OPTIMIZED MATERIALIZED VIEWS
-- =====================================

-- ANSWERS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.answers CASCADE;
CREATE MATERIALIZED VIEW data_views.answers AS
WITH jurisdiction_agg AS (
    SELECT 
        m2m."Answers_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions",
        STRING_AGG(j."Legal_Family", ' | ' ORDER BY j."Legal_Family") AS "Legal_Families",
        MIN(j."Alpha_3_Code") AS "Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" m2m
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Answers_id"
),
questions_agg AS (
    SELECT 
        m2m."Answers_id",
        STRING_AGG(q."Question", ' | ' ORDER BY q.id) AS "Questions",
        STRING_AGG(DISTINCT t."Theme", ' | ' ORDER BY t."Theme") AS "Themes",
        MIN(q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" m2m
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = m2m."Questions_id"
    LEFT JOIN p1q5x3pj29vkrdr."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = q.id
    LEFT JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tq."Themes_id"
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
    -- sort_date based on Last Modified (YYYY-MM-DD)
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
FROM p1q5x3pj29vkrdr."Answers" a
LEFT JOIN jurisdiction_agg ja ON ja."Answers_id" = a.id
LEFT JOIN questions_agg qa ON qa."Answers_id" = a.id;

CREATE INDEX idx_fts_answers ON data_views.answers USING GIN(document);
CREATE UNIQUE INDEX idx_answers_id ON data_views.answers(id);

-- HCCH ANSWERS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.hcch_answers CASCADE;
CREATE MATERIALIZED VIEW data_views.hcch_answers AS
WITH themes_agg AS (
    SELECT 
        m2m."HCCH_Answers_id",
        STRING_AGG(t."Theme", ' | ' ORDER BY t."Theme") AS "Themes"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_HCCH_Answers" m2m
    JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = m2m."Themes_id"
    GROUP BY m2m."HCCH_Answers_id"
),
international_instruments_agg AS (
    SELECT 
        m2m."HCCH_Answers_id",
        STRING_AGG(ii."Name", ' | ' ORDER BY ii."Name") AS "International_Instruments"
    FROM p1q5x3pj29vkrdr."_nc_m2m_HCCH_Answers_International_I" m2m
    JOIN p1q5x3pj29vkrdr."International_Instruments" ii ON ii.id = m2m."International_Instruments_id"
    GROUP BY m2m."HCCH_Answers_id"
),
questions_cold_agg AS (
    SELECT
        qa."Answers_id",
        MIN(q."Question_Number" || '-' || q."Primary_Theme") AS "Question_CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qa."Questions_id"
    GROUP BY qa."Answers_id"
)
SELECT 
    ha.id,
    ha."Adapted_Question",
    ha."Position",
    'HCCH Answers' AS "Table_Synonyms",
    COALESCE(ta."Themes", '') AS "Themes",
    COALESCE(iia."International_Instruments", '') AS "International_Instruments",
    ('HCCH-' || COALESCE(qca."Question_CoLD_ID",'')) AS "CoLD_ID",
    -- sort_date based on Last Modified (YYYY-MM-DD)
    ha."updated_at"::date AS sort_date,
    to_tsvector('english', 
        'HCCH Answers' || ' ' ||
        COALESCE(ha."Adapted_Question", '') || ' ' ||
        COALESCE(ha."Position", '') || ' ' ||
        COALESCE(ta."Themes", '') || ' ' ||
        COALESCE(iia."International_Instruments", '') || ' ' ||
        COALESCE(('HCCH-' || COALESCE(qca."Question_CoLD_ID",'')), '')
    ) AS document
FROM p1q5x3pj29vkrdr."HCCH_Answers" ha
LEFT JOIN themes_agg ta ON ta."HCCH_Answers_id" = ha.id
LEFT JOIN international_instruments_agg iia ON iia."HCCH_Answers_id" = ha.id
LEFT JOIN questions_cold_agg qca ON qca."Answers_id" = ha.id;

CREATE INDEX idx_fts_hcch_answers ON data_views.hcch_answers USING GIN(document);
CREATE UNIQUE INDEX idx_hcch_answers_id ON data_views.hcch_answers(id);

-- COURT DECISIONS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.court_decisions CASCADE;
CREATE MATERIALIZED VIEW data_views.court_decisions AS
WITH jurisdiction_agg AS (
    SELECT 
        m2m."Court_Decisions_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions",
        STRING_AGG(j."Legal_Family", ' | ' ORDER BY j."Legal_Family") AS "Legal_Families",
        MIN(j."Alpha_3_Code") AS "Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" m2m
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Court_Decisions_id"
),
themes_agg AS (
    SELECT
        m2m."Court_Decisions_id",
        STRING_AGG(DISTINCT t."Theme", ' | ' ORDER BY t."Theme") AS "Themes"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Court_Decisions" m2m
    JOIN p1q5x3pj29vkrdr."_nc_m2m_Themes_Questions" tq ON tq."Questions_id" = m2m."Questions_id"
    JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = tq."Themes_id"
    GROUP BY m2m."Court_Decisions_id"
)
SELECT 
    cd.id,
    cd."Case_Citation",
    cd."Case_Rank"::text AS "Case_Rank",
    cd."English_Translation",
    'Court Decisions Case Precedent' AS "Table_Synonyms",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(ja."Legal_Families", '') AS "Legal_Families",
    COALESCE(ta."Themes", '') AS "Themes",
    ('CD-' || COALESCE(ja."Alpha_3_Code", '') || '-' || cd."ID_Number") AS "CoLD_ID",
    -- sort_date based on the text "Date" column (YYYY or DD.MM.YYYY)
    CASE
      WHEN cd."Date" ~ '^[0-9]{4}$'
        THEN to_date(cd."Date", 'YYYY')
      WHEN cd."Date" ~ '^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$'
        THEN to_date(cd."Date", 'DD.MM.YYYY')
      ELSE NULL
    END AS sort_date,
    to_tsvector('english',
        'Court Decisions Case Precedent' || ' ' ||
        COALESCE(cd."Case_Citation", '') || ' ' ||
        COALESCE(cd."Case_Rank"::text, '') || ' ' ||
        COALESCE(cd."English_Translation", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(ja."Legal_Families", '') || ' ' ||
        COALESCE(ta."Themes", '') || ' ' ||
        COALESCE(('CD-' || COALESCE(ja."Alpha_3_Code", '') || '-' || cd."ID_Number"), '')
    ) AS document
FROM p1q5x3pj29vkrdr."Court_Decisions" cd
LEFT JOIN jurisdiction_agg ja ON ja."Court_Decisions_id" = cd.id
LEFT JOIN themes_agg ta ON ta."Court_Decisions_id" = cd.id;

CREATE INDEX idx_fts_court_decisions ON data_views.court_decisions USING GIN(document);
CREATE UNIQUE INDEX idx_court_decisions_id ON data_views.court_decisions(id);

-- DOMESTIC INSTRUMENTS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.domestic_instruments CASCADE;
CREATE MATERIALIZED VIEW data_views.domestic_instruments AS
WITH jurisdiction_agg AS (
    SELECT 
        m2m."Domestic_Instruments_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions",
        MIN(j."Alpha_3_Code") AS "Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Domestic_Instru" m2m
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Domestic_Instruments_id"
),
domestic_legal_provisions_agg AS (
    SELECT
        m2m."Domestic_Instruments_id",
        STRING_AGG(dlp."Full_Text_of_the_Provision__Original_Language_", ' | ' ORDER BY dlp.id) AS "Original_Language_Provisions",
        STRING_AGG(dlp."Full_Text_of_the_Provision__English_Translation_", ' | ' ORDER BY dlp.id) AS "English_Translation_Provisions"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Domestic_Instru_Domestic_Legal_" m2m
    JOIN p1q5x3pj29vkrdr."Domestic_Legal_Provisions" dlp ON dlp.id = m2m."Domestic_Legal_Provisions_id"
    GROUP BY m2m."Domestic_Instruments_id"
),
questions_agg AS (
    SELECT 
        m2m."Domestic_Instruments_id",
        STRING_AGG(q."Question", ' | ' ORDER BY q.id) AS "Questions"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Domestic_Instru" m2m
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = m2m."Questions_id"
    GROUP BY m2m."Domestic_Instruments_id"
)
SELECT 
    di.id,
    di."Title__in_English_",
    di."Official_Title",
    di."Relevant_Provisions",
    di."Full_Text_of_the_Provisions",
    di."Publication_Date",
    di."Entry_Into_Force",
    di."Abbreviation",
    'Domestic Instruments Law Statute' AS "Table_Synonyms",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(dlpa."Original_Language_Provisions", '') AS "Legal_Provisions_Original",
    COALESCE(dlpa."English_Translation_Provisions", '') AS "Legal_Provisions_English",
    -- CoLD_ID
    ('DI-' || COALESCE(ja."Alpha_3_Code", '') || '-' || di."ID_Number") AS "CoLD_ID",
    -- sort_date based on the text "Date" column (YYYY)
    CASE
      WHEN di."Date" ~ '^[0-9]{4}$'
        THEN to_date(di."Date", 'YYYY')
      ELSE NULL
    END AS sort_date,
    to_tsvector('english', 
        'Domestic Instruments Law Statute' || ' ' ||
        COALESCE(di."Title__in_English_", '') || ' ' || 
        COALESCE(di."Official_Title", '') || ' ' || 
        COALESCE(di."Relevant_Provisions", '') || ' ' ||
        COALESCE(di."Full_Text_of_the_Provisions", '') || ' ' ||
        COALESCE(di."Abbreviation", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(dlpa."Original_Language_Provisions", '') || ' ' ||
        COALESCE(dlpa."English_Translation_Provisions", '') || ' ' ||
        COALESCE(qa."Questions", '') || ' ' ||
        COALESCE(('DI-' || COALESCE(ja."Alpha_3_Code", '') || '-' || di."ID_Number"), '')
    ) AS document
FROM p1q5x3pj29vkrdr."Domestic_Instruments" di
LEFT JOIN jurisdiction_agg ja ON ja."Domestic_Instruments_id" = di.id
LEFT JOIN domestic_legal_provisions_agg dlpa ON dlpa."Domestic_Instruments_id" = di.id
LEFT JOIN questions_agg qa ON qa."Domestic_Instruments_id" = di.id;

CREATE INDEX idx_fts_domestic_instruments ON data_views.domestic_instruments USING GIN(document);
CREATE UNIQUE INDEX idx_domestic_instruments_id ON data_views.domestic_instruments(id);

-- REGIONAL INSTRUMENTS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.regional_instruments CASCADE;
CREATE MATERIALIZED VIEW data_views.regional_instruments AS
WITH specialists_agg AS (
    SELECT 
        m2m."Regional_Instruments_id",
        STRING_AGG(s."Specialist", ' | ' ORDER BY s."Specialist") AS "Specialists"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Regional_Instru_Specialists" m2m
    JOIN p1q5x3pj29vkrdr."Specialists" s ON s.id = m2m."Specialists_id"
    GROUP BY m2m."Regional_Instruments_id"
)
SELECT 
    ri.id,
    ri."Abbreviation",
    ri."Title",
    COALESCE(sa."Specialists", '') AS "Specialists",
    'Regional Instruments Regional Agreement Protocol' AS "Table_Synonyms",
    -- CoLD_ID
    ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS "CoLD_ID",
    ri."Date" AS sort_date,
    to_tsvector('english', 
        'Regional Instruments Regional Agreement Protocol' || ' ' ||
        COALESCE(ri."Abbreviation", '') || ' ' || 
        COALESCE(ri."Title", '') || ' ' || 
        COALESCE(sa."Specialists", '') || ' ' ||
        COALESCE(ri."Date"::text, '') || ' ' ||
        ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number")
    ) AS document
FROM p1q5x3pj29vkrdr."Regional_Instruments" ri
LEFT JOIN specialists_agg sa ON sa."Regional_Instruments_id" = ri.id;

CREATE INDEX idx_fts_regional_instruments ON data_views.regional_instruments USING GIN(document);
CREATE UNIQUE INDEX idx_regional_instruments_id ON data_views.regional_instruments(id);

-- INTERNATIONAL INSTRUMENTS SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.international_instruments CASCADE;
CREATE MATERIALIZED VIEW data_views.international_instruments AS
WITH specialists_agg AS (
    SELECT 
        m2m."International_Instruments_id",
        STRING_AGG(s."Specialist", ' | ' ORDER BY s."Specialist") AS "Specialists"
    FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_Specialists" m2m
    JOIN p1q5x3pj29vkrdr."Specialists" s ON s.id = m2m."Specialists_id"
    GROUP BY m2m."International_Instruments_id"
)
SELECT 
    ii.id,
    ii."Name",
    COALESCE(sa."Specialists", '') AS "Specialists",
    'International Instruments Treaty Convention' AS "Table_Synonyms",
    -- CoLD_ID
    ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS "CoLD_ID",
    ii."Date" AS sort_date,
    to_tsvector('english', 
        'International Instruments Treaty Convention' || ' ' ||
        COALESCE(ii."Name", '') || ' ' || 
        COALESCE(sa."Specialists", '') || ' ' ||
        COALESCE(ii."Date"::text, '') || ' ' ||
        ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number")
    ) AS document
FROM p1q5x3pj29vkrdr."International_Instruments" ii
LEFT JOIN specialists_agg sa ON sa."International_Instruments_id" = ii.id;

CREATE INDEX idx_fts_international_instruments ON data_views.international_instruments USING GIN(document);
CREATE UNIQUE INDEX idx_international_instruments_id ON data_views.international_instruments(id);

-- LITERATURE SEARCH VIEW
DROP MATERIALIZED VIEW IF EXISTS data_views.literature CASCADE;
CREATE MATERIALIZED VIEW data_views.literature AS
WITH jurisdiction_agg AS (
    SELECT 
        m2m."Literature_id",
        STRING_AGG(j."Name", ' | ' ORDER BY j."Name") AS "Jurisdictions"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Literature" m2m
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = m2m."Jurisdictions_id"
    GROUP BY m2m."Literature_id"
),
themes_agg AS (
    SELECT 
        m2m."Literature_id",
        STRING_AGG(t."Theme", ' | ' ORDER BY t."Theme") AS "Themes"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Themes_Literature" m2m
    JOIN p1q5x3pj29vkrdr."Themes" t ON t.id = m2m."Themes_id"
    GROUP BY m2m."Literature_id"
)
SELECT 
    l.id,
    l."Title",
    l."Author",
    l."Publication_Year",
    l."Item_Type",
    l."Publication_Title",
    l."Abstract_Note",
    l."ISBN",
    l."ISSN",
    l."DOI",
    l."Url",
    l."Publisher",
    COALESCE(ja."Jurisdictions", '') AS "Jurisdictions",
    COALESCE(ta."Themes", '') AS "Themes",
    ('L-' || l."ID_Number") AS "CoLD_ID",
    CASE
      WHEN l."Publication_Year"::text ~ '^[0-9]{4}$'
        THEN to_date(l."Publication_Year"::text, 'YYYY')
      ELSE NULL
    END AS sort_date,
    'Literature Publication Article' AS "Table_Synonyms",
    to_tsvector('english', 
        'Literature Publication Article' || ' ' ||
        COALESCE(l."Title", '') || ' ' || 
        COALESCE(l."Author", '') || ' ' || 
        COALESCE(l."Publication_Title", '') || ' ' || 
        COALESCE(l."Abstract_Note", '') || ' ' ||
        COALESCE(l."Publisher", '') || ' ' ||
        COALESCE(ja."Jurisdictions", '') || ' ' ||
        COALESCE(ta."Themes", '') || ' ' ||
        ('L-' || l."ID_Number")
    ) AS document
FROM p1q5x3pj29vkrdr."Literature" l
LEFT JOIN jurisdiction_agg ja ON ja."Literature_id" = l.id
LEFT JOIN themes_agg ta ON ta."Literature_id" = l.id;

CREATE INDEX idx_fts_literature ON data_views.literature USING GIN(document);
CREATE UNIQUE INDEX idx_literature_id ON data_views.literature(id);

-- Create search_all function for the data_views schema
DROP FUNCTION IF EXISTS data_views.search_all(text, text[], text[], text[], integer, integer);
DROP FUNCTION IF EXISTS data_views.search_all(text, text[], text[], text[], integer, integer, boolean);

-- Create a new function that returns complete records
CREATE OR REPLACE FUNCTION data_views.search_all(
    search_term TEXT,
    filter_tables TEXT[] DEFAULT NULL,
    filter_jurisdictions TEXT[] DEFAULT NULL,
    filter_themes TEXT[] DEFAULT NULL,
    page INT DEFAULT 1,
    page_size INT DEFAULT 50,
    sort_by_date BOOLEAN DEFAULT TRUE
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
        -- Search Answers with complete data
        SELECT 
            'Answers' AS table_name,
            a.id AS record_id,
            to_jsonb(a.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.answers_complete a
        JOIN data_views.answers search_view ON search_view.id = a.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Answers' = ANY(filter_tables))
        -- THE FOLLOWING BLOCK REMOVES ALL ANSWERS WHERE THE JURISDICTION IS IRRELEVANT!
        --
        AND NOT EXISTS (
            SELECT 1 FROM jsonb_array_elements(a.related_jurisdictions) AS elem
            WHERE COALESCE((elem->>'Irrelevant_')::boolean, FALSE) = TRUE
        )
        --
        --
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))
        -- Exclude answers with "No data"
          AND NOT (btrim(COALESCE(a."Answer", '')) ILIKE '%no data%')

        UNION ALL

        -- Search HCCH_Answers with complete data
        SELECT 
            'HCCH Answers' AS table_name,
            ha.id AS record_id,
            to_jsonb(ha.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.hcch_answers_complete ha
        JOIN data_views.hcch_answers search_view ON search_view.id = ha.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'HCCH Answers' = ANY(filter_tables))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        -- Search Court Decisions with complete data
        SELECT 
            'Court Decisions' AS table_name,
            cd.id AS record_id,
            to_jsonb(cd.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.court_decisions_complete cd
        JOIN data_views.court_decisions search_view ON search_view.id = cd.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Court Decisions' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        -- Search Domestic Instruments with complete data
        SELECT 
            'Domestic Instruments' AS table_name,
            di.id AS record_id,
            to_jsonb(di.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.domestic_instruments_complete di
        JOIN data_views.domestic_instruments search_view ON search_view.id = di.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Domestic Instruments' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))

        UNION ALL

        -- Search Regional Instruments with complete data
        SELECT 
            'Regional Instruments' AS table_name,
            ri.id AS record_id,
            to_jsonb(ri.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.regional_instruments_complete ri
        JOIN data_views.regional_instruments search_view ON search_view.id = ri.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Regional Instruments' = ANY(filter_tables))

        UNION ALL

        -- Search International Instruments with complete data
        SELECT 
            'International Instruments' AS table_name,
            ii.id AS record_id,
            to_jsonb(ii.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.international_instruments_complete ii
        JOIN data_views.international_instruments search_view ON search_view.id = ii.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'International Instruments' = ANY(filter_tables))

        UNION ALL

        -- Search Literature with complete data
        SELECT 
            'Literature' AS table_name,
            l.id AS record_id,
            to_jsonb(l.*) AS complete_record,
            CASE WHEN empty_term THEN 1.0 
                 ELSE ts_rank(search_view.document, plainto_tsquery('english', search_term)) 
            END AS rank,
            search_view.sort_date AS result_date
        FROM data_views.literature_complete l
        JOIN data_views.literature search_view ON search_view.id = l.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Literature' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

    ) AS sub
    ORDER BY
        -- Bucket results to enforce special ordering rules:
        -- 0 = normal results, 1 = low-ranked Court Decisions (Case_Rank <= 5)
        -- Low-ranked Court Decisions are deprioritized to appear after other results.
        CASE
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'Case_Rank')::numeric, 1000000) <= 5
            THEN 1
            ELSE 0
        END ASC,
        -- Within the low-ranked Court Decisions bucket, sort by Case_Rank DESC (5,4,...,1,null)
        CASE
            WHEN sub.table_name = 'Court Decisions'
                 AND COALESCE((sub.complete_record->>'Case_Rank')::numeric, 1000000) <= 5
            THEN COALESCE((sub.complete_record->>'Case_Rank')::numeric, -1)
        END DESC NULLS LAST,
        CASE WHEN sort_by_date THEN sub.result_date ELSE NULL END DESC NULLS LAST,
        sub.rank DESC,
        sub.table_name
    LIMIT page_size OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;

-- Add documentation for the search function
COMMENT ON FUNCTION data_views.search_all IS 
'Search across all data_views materialized views and return complete records.
Parameters:
- search_term: Text to search for
- filter_tables: Array of table names to search within
- filter_jurisdictions: Array of jurisdictions to filter by
- filter_themes: Array of themes to filter by
- page: Page number (starting at 1)
- page_size: Number of results per page
- sort_by_date: Whether to sort by date (true) or relevance (false)

Usage example:
SELECT * FROM data_views.search_all(
   search_term => ''''::text,
   filter_tables => ARRAY[''Literature'']::text[],
   filter_jurisdictions => ARRAY[''Switzerland'',''France'']::text[],
   filter_themes => ARRAY[''Public policy'',''Party autonomy'']::text[],
   page => 1,
   page_size => 10,
   sort_by_date => FALSE
);

Created by: simonweigold on 2025-07-26 14:33:15 UTC';

-- Drop old version, if exists
DROP FUNCTION IF EXISTS data_views.search_for_entry(TEXT, TEXT);

-- Function: data_views.search_for_entry
-- Purpose: Given a table name and a CoLD_ID value, return the complete record and all "hop-1" (directly related) entries as they are defined in the *_complete materialized views.
-- This function returns a set of (found_table, record_id, complete_record, hop1_relations JSONB) rows.

CREATE OR REPLACE FUNCTION data_views.search_for_entry(
    table_name TEXT,
    cold_id TEXT
)
RETURNS TABLE (
    found_table TEXT,
    record_id INTEGER,
    complete_record JSONB,
    hop1_relations JSONB
) AS $$
DECLARE
    rec_id INTEGER;
    rec JSONB;
    hop1 JSONB;
BEGIN
    -- Answers
    IF table_name = 'Answers' THEN
        SELECT id, to_jsonb(a.*)
        INTO rec_id, rec
        FROM data_views.answers_complete a
        WHERE a."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_questions', a.related_questions,
                'related_jurisdictions', a.related_jurisdictions,
                'related_themes', a.related_themes,
                'related_court_decisions', a.related_court_decisions,
                'related_literature', a.related_literature,
                'related_domestic_instruments', a.related_domestic_instruments,
                'related_domestic_legal_provisions', a.related_domestic_legal_provisions
            )
        INTO hop1
        FROM data_views.answers_complete a
        WHERE a."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Answers', rec_id, rec, hop1;

    -- HCCH Answers
    ELSIF table_name = 'HCCH Answers' THEN
        SELECT id, to_jsonb(ha.*)
        INTO rec_id, rec
        FROM data_views.hcch_answers_complete ha
        WHERE ha."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_themes', ha.related_themes,
                'related_international_instruments', ha.related_international_instruments
            )
        INTO hop1
        FROM data_views.hcch_answers_complete ha
        WHERE ha."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'HCCH Answers', rec_id, rec, hop1;

    -- Court Decisions
    ELSIF table_name = 'Court Decisions' THEN
        SELECT id, to_jsonb(cd.*)
        INTO rec_id, rec
        FROM data_views.court_decisions_complete cd
        WHERE cd."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_jurisdictions', cd.related_jurisdictions,
                'related_questions', cd.related_questions,
                'related_answers', cd.related_answers,
                'related_themes', cd.related_themes
            )
        INTO hop1
        FROM data_views.court_decisions_complete cd
        WHERE cd."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Court Decisions', rec_id, rec, hop1;

    -- Domestic Instruments
    ELSIF table_name = 'Domestic Instruments' THEN
        SELECT id, to_jsonb(di.*)
        INTO rec_id, rec
        FROM data_views.domestic_instruments_complete di
        WHERE di."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_jurisdictions', di.related_jurisdictions,
                'related_legal_provisions', di.related_legal_provisions,
                'related_questions', di.related_questions
            )
        INTO hop1
        FROM data_views.domestic_instruments_complete di
        WHERE di."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Domestic Instruments', rec_id, rec, hop1;

    -- Domestic Legal Provisions
    ELSIF table_name = 'Domestic Legal Provisions' THEN
        SELECT id, to_jsonb(dlp.*)
        INTO rec_id, rec
        FROM data_views.domestic_legal_provisions_complete dlp
        WHERE dlp."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_domestic_instruments', dlp.related_domestic_instruments
            )
        INTO hop1
        FROM data_views.domestic_legal_provisions_complete dlp
        WHERE dlp."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Domestic Legal Provisions', rec_id, rec, hop1;

    -- Regional Instruments
    ELSIF table_name = 'Regional Instruments' THEN
        SELECT id, to_jsonb(ri.*)
        INTO rec_id, rec
        FROM data_views.regional_instruments_complete ri
        WHERE ri."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_specialists', ri.related_specialists,
                'related_legal_provisions', ri.related_legal_provisions
            )
        INTO hop1
        FROM data_views.regional_instruments_complete ri
        WHERE ri."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Regional Instruments', rec_id, rec, hop1;

    -- Regional Legal Provisions
    ELSIF table_name = 'Regional Legal Provisions' THEN
        SELECT id, to_jsonb(rlp.*)
        INTO rec_id, rec
        FROM data_views.regional_legal_provisions_complete rlp
        WHERE rlp."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'Instrument_CoLD_ID', rlp."Instrument_CoLD_ID",
                'related_regional_instruments', rlp.related_regional_instruments
            )
        INTO hop1
        FROM data_views.regional_legal_provisions_complete rlp
        WHERE rlp."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Regional Legal Provisions', rec_id, rec, hop1;

    -- International Instruments
    ELSIF table_name = 'International Instruments' THEN
        SELECT id, to_jsonb(ii.*)
        INTO rec_id, rec
        FROM data_views.international_instruments_complete ii
        WHERE ii."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_specialists', ii.related_specialists,
                'related_hcch_answers', ii.related_hcch_answers,
                'related_legal_provisions', ii.related_legal_provisions,
                'related_literature', ii.related_literature
            )
        INTO hop1
        FROM data_views.international_instruments_complete ii
        WHERE ii."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'International Instruments', rec_id, rec, hop1;

    -- International Legal Provisions
    ELSIF table_name = 'International Legal Provisions' THEN
        SELECT id, to_jsonb(ilp.*)
        INTO rec_id, rec
        FROM data_views.international_legal_provisions_complete ilp
        WHERE ilp."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'Instrument_CoLD_ID', ilp."Instrument_CoLD_ID"
            )
        INTO hop1
        FROM data_views.international_legal_provisions_complete ilp
        WHERE ilp."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'International Legal Provisions', rec_id, rec, hop1;

    -- Literature
    ELSIF table_name = 'Literature' THEN
        SELECT id, to_jsonb(l.*)
        INTO rec_id, rec
        FROM data_views.literature_complete l
        WHERE l."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_jurisdictions', l.related_jurisdictions,
                'related_themes', l.related_themes
            )
        INTO hop1
        FROM data_views.literature_complete l
        WHERE l."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Literature', rec_id, rec, hop1;

    -- Arbitral Awards
    ELSIF table_name = 'Arbitral Awards' THEN
        SELECT id, to_jsonb(aa.*)
        INTO rec_id, rec
        FROM data_views.arbitral_awards_complete aa
        WHERE aa."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_arbitral_institutions', aa.related_arbitral_institutions,
                'related_arbitral_provisions', aa.related_arbitral_provisions,
                'related_court_decisions', aa.related_court_decisions,
                'related_jurisdictions', aa.related_jurisdictions,
                'related_themes', aa.related_themes
            )
        INTO hop1
        FROM data_views.arbitral_awards_complete aa
        WHERE aa."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Awards', rec_id, rec, hop1;

    -- Arbitral Institutions (no CoLD_ID; resolve by id)
    ELSIF table_name = 'Arbitral Institutions' THEN
        SELECT id, to_jsonb(ai.*)
        INTO rec_id, rec
        FROM data_views.arbitral_institutions_complete ai
        WHERE ai.id::text = cold_id
           OR ('AI-' || ai.id::text) = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_arbitral_awards', ai.related_arbitral_awards,
                'related_arbitral_rules', ai.related_arbitral_rules,
                'related_arbitral_provisions', ai.related_arbitral_provisions,
                'related_jurisdictions', ai.related_jurisdictions
            )
        INTO hop1
    FROM data_views.arbitral_institutions_complete ai
    WHERE ai.id::text = cold_id
       OR ('AI-' || ai.id::text) = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Institutions', rec_id, rec, hop1;

    -- Arbitral Rules
    ELSIF table_name = 'Arbitral Rules' THEN
        SELECT id, to_jsonb(ar.*)
        INTO rec_id, rec
        FROM data_views.arbitral_rules_complete ar
        WHERE ar."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_arbitral_institutions', ar.related_arbitral_institutions,
                'related_arbitral_provisions', ar.related_arbitral_provisions,
                'related_jurisdictions', ar.related_jurisdictions
            )
        INTO hop1
        FROM data_views.arbitral_rules_complete ar
        WHERE ar."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Rules', rec_id, rec, hop1;

    -- Arbitral Provisions
    ELSIF table_name = 'Arbitral Provisions' THEN
        SELECT id, to_jsonb(ap.*)
        INTO rec_id, rec
        FROM data_views.arbitral_provisions_complete ap
        WHERE ap."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_arbitral_awards', ap.related_arbitral_awards,
                'related_arbitral_institutions', ap.related_arbitral_institutions,
                'related_arbitral_rules', ap.related_arbitral_rules
            )
        INTO hop1
        FROM data_views.arbitral_provisions_complete ap
        WHERE ap."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Provisions', rec_id, rec, hop1;

    -- Jurisdictions
    ELSIF table_name = 'Jurisdictions' THEN
        SELECT id, to_jsonb(j.*)
        INTO rec_id, rec
        FROM data_views.jurisdictions_complete j
        WHERE j."Alpha_3_Code" = cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'related_answers', j.related_answers,
            'related_domestic_instruments', j.related_domestic_instruments,
            'related_court_decisions', j.related_court_decisions,
            'related_literature', j.related_literature,
            'related_specialists', j.related_specialists
        )
        INTO hop1
        FROM data_views.jurisdictions_complete j
        WHERE j."Alpha_3_Code" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Jurisdictions', rec_id, rec, hop1;

    -- Questions
    ELSIF table_name = 'Questions' THEN
        SELECT id, to_jsonb(q.*)
        INTO rec_id, rec
        FROM data_views.questions_complete q
        WHERE q."CoLD_ID" = cold_id
        LIMIT 1;

        SELECT 
            jsonb_build_object(
                'related_themes', q.related_themes,
                'related_answers', q.related_answers,
                'related_court_decisions', q.related_court_decisions,
                'related_domestic_instruments', q.related_domestic_instruments
            )
        INTO hop1
        FROM data_views.questions_complete q
        WHERE q."CoLD_ID" = cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Questions', rec_id, rec, hop1;

    ELSE
        RAISE EXCEPTION 'Unsupported table_name: %', table_name;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION data_views.search_for_entry IS
'Given a table name and a CoLD_ID value, returns the complete record (from the *_complete materialized view) and all first-degree (hop-1) related entries as JSONB, following the structure of *_complete views. The returned column found_table avoids parameter collision.';
-- example usage:
-- SELECT * FROM data_views.search_for_entry('Answers', 'CHE_01.1-P');
-- SELECT * FROM data_views.search_for_entry('Court Decisions', 'CD-CHE-1020');

-- Initial refresh of all materialized views
SELECT data_views.refresh_all_materialized_views();