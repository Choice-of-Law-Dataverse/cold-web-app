from __future__ import annotations

from alembic import op

revision = "202603081100"
down_revision = "202603081000"
branch_labels = None
depends_on = None

SCHEMA = "p1q5x3pj29vkrdr"

BASE_QUESTIONS = f"""
CREATE OR REPLACE VIEW data_views.base_questions AS
SELECT
    q.id,
    q."Question" AS question,
    q."Question_Number" AS question_number,
    q."Primary_Theme" AS primary_theme,
    q."Answering_Options" AS answering_options,
    (q."Question_Number" || '-' || q."Primary_Theme") AS cold_id,
    q.created_at,
    q.updated_at,
    q.created_by,
    q.updated_by
FROM {SCHEMA}."Questions" q;
"""

BASE_ANSWERS = f"""
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
    a.updated_by
FROM {SCHEMA}."Answers" a
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
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

BASE_HCCH_ANSWERS = f"""
CREATE OR REPLACE VIEW data_views.base_hcch_answers AS
SELECT
    ha.id,
    ha."Adapted_Question" AS adapted_question,
    ha."Position" AS position,
    qcold."CoLD_ID" AS question_cold_id,
    ('HCCH-' || COALESCE(qcold."CoLD_ID", '')) AS cold_id,
    ha.created_at,
    ha.updated_at,
    ha.created_by,
    ha.updated_by
FROM {SCHEMA}."HCCH_Answers" ha
LEFT JOIN LATERAL (
    SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_Questions_HCCH_Answers" qa
    JOIN {SCHEMA}."Questions" q ON q.id = qa."Questions_id"
    WHERE qa."HCCH_Answers_id" = ha.id
    ORDER BY q.id
    LIMIT 1
) qcold ON true;
"""

BASE_COURT_DECISIONS = f"""
CREATE OR REPLACE VIEW data_views.base_court_decisions AS
SELECT
    cd.id,
    cd."ID_Number" AS id_number,
    cd."Case_Citation" AS case_citation,
    cd."Case_Title" AS case_title,
    cd."Instance" AS instance,
    cd."Date" AS date,
    cd."Abstract" AS abstract,
    cd."Case_Rank" AS case_rank,
    cd."English_Translation" AS english_translation,
    cd."Choice_of_Law_Issue" AS choice_of_law_issue,
    cd."Court_s_Position" AS court_s_position,
    cd."Translated_Excerpt" AS translated_excerpt,
    cd."Relevant_Facts" AS relevant_facts,
    cd."Date_of_Judgment" AS date_of_judgment,
    cd."PIL_Provisions" AS pil_provisions,
    cd."Original_Text" AS original_text,
    cd."Quote" AS quote,
    cd."Text_of_the_Relevant_Legal_Provisions" AS text_of_the_relevant_legal_provisions,
    cd."Official_Source__URL_" AS official_source_url,
    cd."Official_Source__PDF_" AS official_source_pdf,
    cd."Publication_Date_ISO" AS publication_date_iso,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    ('CD-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || cd."ID_Number") AS cold_id,
    cd.created_at,
    cd.updated_at,
    cd.created_by,
    cd.updated_by
FROM {SCHEMA}."Court_Decisions" cd
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM {SCHEMA}."_nc_m2m_Jurisdictions_Court_Decisions" jcd
    JOIN {SCHEMA}."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
    WHERE jcd."Court_Decisions_id" = cd.id
    ORDER BY j.id
    LIMIT 1
) jcodes ON true;
"""

BASE_DOMESTIC_INSTRUMENTS = f"""
CREATE OR REPLACE VIEW data_views.base_domestic_instruments AS
SELECT
    di.id,
    di."ID_Number" AS id_number,
    di."Title__in_English_" AS title_in_english,
    di."Official_Title" AS official_title,
    di."Date" AS date,
    di."Status" AS status,
    di."Abbreviation" AS abbreviation,
    di."Relevant_Provisions" AS relevant_provisions,
    di."Full_Text_of_the_Provisions" AS full_text_of_the_provisions,
    di."Publication_Date" AS publication_date,
    di."Entry_Into_Force" AS entry_into_force,
    di."Source__URL_" AS source_url,
    di."Source__PDF_" AS source_pdf,
    di."Compatible_With_the_HCCH_Principles_" AS compatible_with_the_hcch_principles,
    di."Compatible_With_the_UNCITRAL_Model_Law_" AS compatible_with_the_uncitral_model_law,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    ('DI-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || di."ID_Number") AS cold_id,
    di.created_at,
    di.updated_at,
    di.created_by,
    di.updated_by
FROM {SCHEMA}."Domestic_Instruments" di
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM {SCHEMA}."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
    JOIN {SCHEMA}."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
    WHERE jdi."Domestic_Instruments_id" = di.id
    ORDER BY j.id
    LIMIT 1
) jcodes ON true;
"""

BASE_DOMESTIC_LEGAL_PROVISIONS = f"""
CREATE OR REPLACE VIEW data_views.base_domestic_legal_provisions AS
SELECT
    dlp.id,
    dlp."Article" AS article,
    dlp."Full_Text_of_the_Provision__Original_Language_" AS full_text_of_the_provision_original_language,
    dlp."Full_Text_of_the_Provision__English_Translation_" AS full_text_of_the_provision_english_translation,
    dlp."Ranking__Display_Order_" AS ranking_display_order,
    di_cold."CoLD_ID" AS domestic_instrument_cold_id,
    (COALESCE(di_cold."CoLD_ID", '') || ' ' || dlp."Article") AS cold_id,
    dlp.created_at,
    dlp.updated_at,
    dlp.created_by,
    dlp.updated_by
FROM {SCHEMA}."Domestic_Legal_Provisions" dlp
LEFT JOIN LATERAL (
    SELECT
        ('DI-' || COALESCE(j."Alpha_3_Code", '') || '-' || di."ID_Number") AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp
    JOIN {SCHEMA}."Domestic_Instruments" di ON di.id = didlp."Domestic_Instruments_id"
    LEFT JOIN {SCHEMA}."_nc_m2m_Jurisdictions_Domestic_Instru" jdi ON jdi."Domestic_Instruments_id" = di.id
    LEFT JOIN {SCHEMA}."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
    WHERE didlp."Domestic_Legal_Provisions_id" = dlp.id
    ORDER BY di.id
    LIMIT 1
) di_cold ON true;
"""

BASE_REGIONAL_INSTRUMENTS = f"""
CREATE OR REPLACE VIEW data_views.base_regional_instruments AS
SELECT
    ri.id,
    ri."ID_Number" AS id_number,
    ri."Title" AS title,
    ri."Abbreviation" AS abbreviation,
    ri."Date" AS date,
    ri."URL" AS url,
    ri."Attachment" AS attachment,
    ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS cold_id,
    ri.created_at,
    ri.updated_at,
    ri.created_by,
    ri.updated_by
FROM {SCHEMA}."Regional_Instruments" ri;
"""

BASE_REGIONAL_LEGAL_PROVISIONS = f"""
CREATE OR REPLACE VIEW data_views.base_regional_legal_provisions AS
SELECT
    rlp.id,
    rlp."Provision" AS provision,
    rlp."Title_of_the_Provision" AS title_of_the_provision,
    rlp."Full_Text" AS full_text,
    ri_cold."CoLD_ID" AS instrument_cold_id,
    (COALESCE(ri_cold."CoLD_ID", '') || ' ' || rlp."Provision") AS cold_id,
    rlp.created_at,
    rlp.updated_at,
    rlp.created_by,
    rlp.updated_by
FROM {SCHEMA}."Regional_Legal_Provisions" rlp
LEFT JOIN LATERAL (
    SELECT ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_Regional_Instru_Regional_Legal_" mirl
    JOIN {SCHEMA}."Regional_Instruments" ri ON ri.id = mirl."Regional_Instruments_id"
    WHERE mirl."Regional_Legal_Provisions_id" = rlp.id
    ORDER BY ri.id
    LIMIT 1
) ri_cold ON true;
"""

BASE_INTERNATIONAL_INSTRUMENTS = f"""
CREATE OR REPLACE VIEW data_views.base_international_instruments AS
SELECT
    ii.id,
    ii."ID_Number" AS id_number,
    ii."Name" AS name,
    ii."Date" AS date,
    ii."URL" AS url,
    ii."Attachment" AS attachment,
    ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS cold_id,
    ii.created_at,
    ii.updated_at,
    ii.created_by,
    ii.updated_by
FROM {SCHEMA}."International_Instruments" ii;
"""

BASE_INTERNATIONAL_LEGAL_PROVISIONS = f"""
CREATE OR REPLACE VIEW data_views.base_international_legal_provisions AS
SELECT
    ilp.id,
    ilp."Provision" AS provision,
    ilp."Title_of_the_Provision" AS title_of_the_provision,
    ilp."Full_Text" AS full_text,
    ilp."Ranking__Display_Order_" AS ranking_display_order,
    ii_cold."CoLD_ID" AS instrument_cold_id,
    (COALESCE(ii_cold."CoLD_ID", '') || ' ' || ilp."Provision") AS cold_id,
    ilp.created_at,
    ilp.updated_at,
    ilp.created_by,
    ilp.updated_by
FROM {SCHEMA}."International_Legal_Provisions" ilp
LEFT JOIN LATERAL (
    SELECT ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_International_I_International_L" miil
    JOIN {SCHEMA}."International_Instruments" ii ON ii.id = miil."International_Instruments_id"
    WHERE miil."International_Legal_Provisions_id" = ilp.id
    ORDER BY ii.id
    LIMIT 1
) ii_cold ON true;
"""

BASE_LITERATURE = f"""
CREATE OR REPLACE VIEW data_views.base_literature AS
SELECT
    l.id,
    l."ID_Number" AS id_number,
    l."Item_Type" AS item_type,
    l."Publication_Year" AS publication_year,
    l."Author" AS author,
    l."Title" AS title,
    l."Publication_Title" AS publication_title,
    l."Abstract_Note" AS abstract_note,
    l."ISBN" AS isbn,
    l."ISSN" AS issn,
    l."DOI" AS doi,
    l."Url" AS url,
    l."Date" AS date,
    l."Date_Added" AS date_added,
    l."Date_Modified" AS date_modified,
    l."Publisher" AS publisher,
    l."Language" AS language,
    l."Extra" AS extra,
    l."Manual_Tags" AS manual_tags,
    l."Editor" AS editor,
    l."Issue" AS issue,
    l."Volume" AS volume,
    l."Pages" AS pages,
    l."Library_Catalog" AS library_catalog,
    l."Access_Date" AS access_date,
    l."Open_Access" AS open_access,
    l."Open_Access_URL" AS open_access_url,
    l."Journal_Abbreviation" AS journal_abbreviation,
    l."Short_Title" AS short_title,
    l."Place" AS place,
    l."Num_Pages" AS num_pages,
    l."Type" AS type,
    l."OUP_JD_Chapter" AS oup_jd_chapter,
    l."Contributor" AS contributor,
    l."Automatic_Tags" AS automatic_tags,
    l."Number" AS number,
    l."Series" AS series,
    l."Series_Number" AS series_number,
    l."Series_Editor" AS series_editor,
    l."Edition" AS edition,
    l."Call_Number" AS call_number,
    l."Jurisdiction_Summary" AS jurisdiction_summary,
    ('L-' || l."ID_Number") AS cold_id,
    l.created_at,
    l.updated_at,
    l.created_by,
    l.updated_by,
    (
        SELECT string_agg(j."Name", ', ')
        FROM {SCHEMA}."_nc_m2m_Jurisdictions_Literature" jl
        JOIN {SCHEMA}."Jurisdictions" j ON j.id = jl."Jurisdictions_id"
        WHERE jl."Literature_id" = l.id
    ) AS jurisdiction
FROM {SCHEMA}."Literature" l;
"""

BASE_ARBITRAL_AWARDS = f"""
CREATE OR REPLACE VIEW data_views.base_arbitral_awards AS
SELECT
    aa.id,
    aa."ID_Number" AS id_number,
    aa."Case_Number" AS case_number,
    aa."Context" AS context,
    aa."Award_Summary" AS award_summary,
    aa."Year" AS year,
    aa."Nature_of_the_Award" AS nature_of_the_award,
    aa."Seat__Town_" AS seat_town,
    aa."Source" AS source,
    ('AA-' || aa."ID_Number") AS cold_id,
    aa.created_at,
    aa.updated_at,
    aa.created_by,
    aa.updated_by
FROM {SCHEMA}."Arbitral_Awards" aa;
"""

BASE_ARBITRAL_INSTITUTIONS = f"""
CREATE OR REPLACE VIEW data_views.base_arbitral_institutions AS
SELECT
    ai.id,
    ai."Institution" AS institution,
    ai."Abbreviation" AS abbreviation,
    ('AI-' || ai.id) AS cold_id,
    ai.created_at,
    ai.updated_at,
    ai.created_by,
    ai.updated_by
FROM {SCHEMA}."Arbitral_Institutions" ai;
"""

BASE_ARBITRAL_RULES = f"""
CREATE OR REPLACE VIEW data_views.base_arbitral_rules AS
SELECT
    ar.id,
    ar."ID_Number" AS id_number,
    ar."Set_of_Rules" AS set_of_rules,
    ar."In_Force_From" AS in_force_from,
    ar."Official_Source__URL_" AS official_source_url,
    ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS cold_id,
    ar.created_at,
    ar.updated_at,
    ar.created_by,
    ar.updated_by
FROM {SCHEMA}."Arbitral_Rules" ar;
"""

BASE_ARBITRAL_PROVISIONS = f"""
CREATE OR REPLACE VIEW data_views.base_arbitral_provisions AS
SELECT
    ap.id,
    ap."Article" AS article,
    ap."Full_Text_of_the_Provision__Original_Language_" AS full_text_original_language,
    ap."Full_Text_of_the_Provision__English_Translation_" AS full_text_english_translation,
    ap."Arbitration_method_type" AS arbitration_method_type,
    ap."Non_State_law_allowed_in_AoC_" AS non_state_law_allowed_in_aoc,
    ar_cold."CoLD_ID" AS arbitral_rules_cold_id,
    (COALESCE(ar_cold."CoLD_ID", '') || ' ' || COALESCE(ap."Article", '')) AS cold_id,
    ap.created_at,
    ap.updated_at,
    ap.created_by,
    ap.updated_by
FROM {SCHEMA}."Arbitral Provisions" ap
LEFT JOIN LATERAL (
    SELECT ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS "CoLD_ID"
    FROM {SCHEMA}."_nc_m2m_Arbitral Provis_Arbitral_Rules" m
    JOIN {SCHEMA}."Arbitral_Rules" ar ON ar.id = m."Arbitral_Rules_id"
    WHERE m."Arbitral Provisions_id" = ap.id
    ORDER BY ar.id
    LIMIT 1
) ar_cold ON true;
"""

BASE_JURISDICTIONS = f"""
CREATE OR REPLACE VIEW data_views.base_jurisdictions AS
SELECT
    j.id,
    j."Name" AS name,
    j."Alpha_3_Code" AS alpha_3_code,
    j."Type" AS type,
    j."Region" AS region,
    j."North_South_Divide" AS north_south_divide,
    j."Jurisdictional_Differentiator" AS jurisdictional_differentiator,
    j."Legal_Family" AS legal_family,
    j."Jurisdiction_Summary" AS jurisdiction_summary,
    j."Irrelevant_" AS irrelevant,
    j."Done" AS done,
    j."Alpha_3_Code" AS cold_id,
    j.created_at,
    j.updated_at,
    j.created_by,
    j.updated_by
FROM {SCHEMA}."Jurisdictions" j;
"""

BASE_SPECIALISTS = f"""
CREATE OR REPLACE VIEW data_views.base_specialists AS
SELECT
    s.id,
    s."Specialist" AS specialist,
    s."Affiliation" AS affiliation,
    s."Contact" AS contact,
    s."Bio" AS bio,
    s."Website" AS website,
    ('SP-' || s.id) AS cold_id,
    s.created_at,
    s.updated_at,
    s.created_by,
    s.updated_by
FROM {SCHEMA}."Specialists" s;
"""

SEARCH_ALL_V3 = f"""
DROP FUNCTION IF EXISTS data_views.search_all_v2(text, text[], text[], text[], integer, integer);
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

SEARCH_ALL_COUNT_V3 = f"""
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
    ) AS sub;

    RETURN total;
END;
$$ LANGUAGE plpgsql STABLE;
"""

DROP_SEARCH_FOR_ENTRY = """
DROP FUNCTION IF EXISTS data_views.search_for_entry_v2(TEXT, TEXT);
"""

BASE_VIEWS = [
    BASE_QUESTIONS,
    BASE_ANSWERS,
    BASE_HCCH_ANSWERS,
    BASE_COURT_DECISIONS,
    BASE_DOMESTIC_INSTRUMENTS,
    BASE_DOMESTIC_LEGAL_PROVISIONS,
    BASE_REGIONAL_INSTRUMENTS,
    BASE_REGIONAL_LEGAL_PROVISIONS,
    BASE_INTERNATIONAL_INSTRUMENTS,
    BASE_INTERNATIONAL_LEGAL_PROVISIONS,
    BASE_LITERATURE,
    BASE_ARBITRAL_AWARDS,
    BASE_ARBITRAL_INSTITUTIONS,
    BASE_ARBITRAL_RULES,
    BASE_ARBITRAL_PROVISIONS,
    BASE_JURISDICTIONS,
    BASE_SPECIALISTS,
]

BASE_VIEW_NAMES = [
    "base_questions",
    "base_answers",
    "base_hcch_answers",
    "base_court_decisions",
    "base_domestic_instruments",
    "base_domestic_legal_provisions",
    "base_regional_instruments",
    "base_regional_legal_provisions",
    "base_international_instruments",
    "base_international_legal_provisions",
    "base_literature",
    "base_arbitral_awards",
    "base_arbitral_institutions",
    "base_arbitral_rules",
    "base_arbitral_provisions",
    "base_jurisdictions",
    "base_specialists",
]


def upgrade() -> None:
    for view_sql in BASE_VIEWS:
        op.execute(view_sql)
    op.execute(SEARCH_ALL_COUNT_V3)
    op.execute(SEARCH_ALL_V3)
    op.execute(DROP_SEARCH_FOR_ENTRY)


def downgrade() -> None:
    for name in BASE_VIEW_NAMES:
        op.execute(f"DROP VIEW IF EXISTS data_views.{name} CASCADE;")
