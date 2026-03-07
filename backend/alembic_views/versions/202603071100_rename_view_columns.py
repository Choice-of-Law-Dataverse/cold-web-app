from __future__ import annotations

from alembic import op

revision = "202603071100"
down_revision = "202603071000"
branch_labels = None
depends_on = None


QUESTIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.questions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.questions_complete AS
SELECT
    q.id,
    q."Question" AS question,
    q."Question_Number" AS question_number,
    q."Primary_Theme" AS primary_theme,
    q."Answering_Options" AS answering_options,
    q."Created" AS created,
    q."ncRecordId" AS nc_record_id,
    q."created_at" AS created_at,
    q."updated_at" AS updated_at,
    q."created_by" AS created_by,
    q."updated_by" AS updated_by,
    q."nc_order" AS nc_order,
    (q."Question_Number" || '-' || q."Primary_Theme") AS cold_id,
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
CREATE INDEX idx_questions_complete_cold_id ON data_views.questions_complete(cold_id);
"""

ANSWERS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.answers_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.answers_complete AS
SELECT
    a.id,
    a."Answer" AS answer,
    a."More_Information" AS more_information,
    a."To_Review_" AS to_review,
    a."OUP_Book_Quote" AS oup_book_quote,
    a."Created" AS created,
    a."ncRecordId" AS nc_record_id,
    a."created_at" AS created_at,
    a."updated_at" AS updated_at,
    a."created_by" AS created_by,
    a."updated_by" AS updated_by,
    a."nc_order" AS nc_order,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    qcold."CoLD_ID" AS question_cold_id,
    (COALESCE(jcodes."Alpha_3_Code", '') || '_' || COALESCE(qcold."CoLD_ID", '')) AS cold_id,
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
                'CoLD_ID', ('CD-' || COALESCE(cd_jcodes."Alpha_3_Code", '') || '-' || COALESCE(cd."ID_Number"::text, ''))
            )
        )
        FROM p1q5x3pj29vkrdr."_nc_m2m_Answers_Court_Decisions" acd
        JOIN p1q5x3pj29vkrdr."Court_Decisions" cd ON cd.id = acd."Court_Decisions_id"
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Court_Decisions" jcd
            JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
            WHERE jcd."Court_Decisions_id" = cd.id
            ORDER BY j.id
            LIMIT 1
        ) cd_jcodes ON true
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
                    'DI-' || COALESCE(di_jcodes."Alpha_3_Code", '') || '-' || COALESCE(di."ID_Number"::text, '')
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
            ORDER BY j.id
            LIMIT 1
        ) di_jcodes ON true
        WHERE adi."Answers_id" = a.id
    ) AS related_domestic_instruments,
    (
        SELECT jsonb_agg(
            to_jsonb(dlp) || jsonb_build_object(
                'CoLD_ID', (
                    'DI-' || COALESCE(dlp_jcodes."Alpha_3_Code", '') || '-' || COALESCE(di."ID_Number"::text, '') || ' ' || COALESCE(dlp."Article", '')
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
            ORDER BY j.id
            LIMIT 1
        ) dlp_jcodes ON true
    ) AS related_domestic_legal_provisions
FROM p1q5x3pj29vkrdr."Answers" a
LEFT JOIN LATERAL (
    SELECT j."Alpha_3_Code"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Jurisdictions_Answers" ja
    JOIN p1q5x3pj29vkrdr."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
    WHERE ja."Answers_id" = a.id
    ORDER BY j.id
    LIMIT 1
) jcodes ON true
LEFT JOIN LATERAL (
    SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_Questions_Answers" qa
    JOIN p1q5x3pj29vkrdr."Questions" q ON q.id = qa."Questions_id"
    WHERE qa."Answers_id" = a.id
    ORDER BY q.id
    LIMIT 1
) qcold ON true;

CREATE UNIQUE INDEX idx_answers_complete_id ON data_views.answers_complete(id);
CREATE INDEX idx_answers_complete_cold_id ON data_views.answers_complete(cold_id);
"""

HCCH_ANSWERS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.hcch_answers_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.hcch_answers_complete AS
SELECT
    ha.id,
    ha."Adapted_Question" AS adapted_question,
    ha."Position" AS position,
    ha."Created" AS created,
    ha."ncRecordId" AS nc_record_id,
    ha."created_at" AS created_at,
    ha."updated_at" AS updated_at,
    ha."created_by" AS created_by,
    ha."updated_by" AS updated_by,
    ha."nc_order" AS nc_order,
    qcold."CoLD_ID" AS question_cold_id,
    ('HCCH-' || COALESCE(qcold."CoLD_ID", '')) AS cold_id,
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
    ORDER BY q.id
    LIMIT 1
) qcold ON true;

CREATE UNIQUE INDEX idx_hcch_answers_complete_id ON data_views.hcch_answers_complete(id);
CREATE INDEX idx_hcch_answers_complete_cold_id ON data_views.hcch_answers_complete(cold_id);
"""

DOMESTIC_INSTRUMENTS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.domestic_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.domestic_instruments_complete AS
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
    di."Created" AS created,
    di."ncRecordId" AS nc_record_id,
    di."created_at" AS created_at,
    di."updated_at" AS updated_at,
    di."created_by" AS created_by,
    di."updated_by" AS updated_by,
    di."nc_order" AS nc_order,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    ('DI-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || di."ID_Number") AS cold_id,
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
    ORDER BY j.id
    LIMIT 1
) jcodes ON true;

CREATE UNIQUE INDEX idx_domestic_instruments_complete_id ON data_views.domestic_instruments_complete(id);
CREATE INDEX idx_domestic_instruments_complete_cold_id ON data_views.domestic_instruments_complete(cold_id);
"""

DOMESTIC_LEGAL_PROVISIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.domestic_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.domestic_legal_provisions_complete AS
SELECT
    dlp.id,
    dlp."Article" AS article,
    dlp."Full_Text_of_the_Provision__Original_Language_" AS full_text_of_the_provision_original_language,
    dlp."Full_Text_of_the_Provision__English_Translation_" AS full_text_of_the_provision_english_translation,
    dlp."Ranking__Display_Order_" AS ranking_display_order,
    dlp."Created" AS created,
    dlp."ncRecordId" AS nc_record_id,
    dlp."created_at" AS created_at,
    dlp."updated_at" AS updated_at,
    dlp."created_by" AS created_by,
    dlp."updated_by" AS updated_by,
    dlp."nc_order" AS nc_order,
    di_cold."CoLD_ID" AS domestic_instrument_cold_id,
    (COALESCE(di_cold."CoLD_ID", '') || ' ' || dlp."Article") AS cold_id,
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
    ORDER BY di.id
    LIMIT 1
) di_cold ON true;

CREATE UNIQUE INDEX idx_domestic_legal_provisions_complete_id ON data_views.domestic_legal_provisions_complete(id);
CREATE INDEX idx_domestic_legal_provisions_complete_cold_id ON data_views.domestic_legal_provisions_complete(cold_id);
"""

REGIONAL_INSTRUMENTS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.regional_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.regional_instruments_complete AS
SELECT
    ri.id,
    ri."ID_Number" AS id_number,
    ri."Title" AS title,
    ri."Abbreviation" AS abbreviation,
    ri."Date" AS date,
    ri."URL" AS url,
    ri."Attachment" AS attachment,
    ri."Created" AS created,
    ri."ncRecordId" AS nc_record_id,
    ri."created_at" AS created_at,
    ri."updated_at" AS updated_at,
    ri."created_by" AS created_by,
    ri."updated_by" AS updated_by,
    ri."nc_order" AS nc_order,
    ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS cold_id,
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
CREATE INDEX idx_regional_instruments_complete_cold_id ON data_views.regional_instruments_complete(cold_id);
"""

REGIONAL_LEGAL_PROVISIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.regional_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.regional_legal_provisions_complete AS
SELECT
    rlp.id,
    rlp."Provision" AS provision,
    rlp."Title_of_the_Provision" AS title_of_the_provision,
    rlp."Full_Text" AS full_text,
    rlp."Created" AS created,
    rlp."ncRecordId" AS nc_record_id,
    rlp."created_at" AS created_at,
    rlp."updated_at" AS updated_at,
    rlp."created_by" AS created_by,
    rlp."updated_by" AS updated_by,
    rlp."nc_order" AS nc_order,
    ri_cold."CoLD_ID" AS instrument_cold_id,
    (COALESCE(ri_cold."CoLD_ID", '') || ' ' || rlp."Provision") AS cold_id,
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
    ORDER BY ri.id
    LIMIT 1
) ri_cold ON true;

CREATE UNIQUE INDEX idx_regional_legal_provisions_complete_id ON data_views.regional_legal_provisions_complete(id);
CREATE INDEX idx_regional_legal_provisions_complete_cold_id ON data_views.regional_legal_provisions_complete(cold_id);
"""

INTERNATIONAL_INSTRUMENTS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.international_instruments_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.international_instruments_complete AS
SELECT
    ii.id,
    ii."ID_Number" AS id_number,
    ii."Name" AS name,
    ii."Title" AS title,
    ii."Title__in_English_" AS title_in_english,
    ii."Abbreviation" AS abbreviation,
    ii."Date" AS date,
    ii."Status" AS status,
    ii."URL" AS url,
    ii."Attachment" AS attachment,
    ii."Entry_Into_Force" AS entry_into_force,
    ii."Publication_Date" AS publication_date,
    ii."Relevant_Provisions" AS relevant_provisions,
    ii."Full_Text_of_the_Provisions" AS full_text_of_the_provisions,
    ii."Created" AS created,
    ii."ncRecordId" AS nc_record_id,
    ii."created_at" AS created_at,
    ii."updated_at" AS updated_at,
    ii."created_by" AS created_by,
    ii."updated_by" AS updated_by,
    ii."nc_order" AS nc_order,
    ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS cold_id,
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
CREATE INDEX idx_international_instruments_complete_cold_id ON data_views.international_instruments_complete(cold_id);
"""

INTERNATIONAL_LEGAL_PROVISIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.international_legal_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.international_legal_provisions_complete AS
SELECT
    ilp.id,
    ilp."Provision" AS provision,
    ilp."Title_of_the_Provision" AS title_of_the_provision,
    ilp."Full_Text" AS full_text,
    ilp."Ranking__Display_Order_" AS ranking_display_order,
    ilp."Created" AS created,
    ilp."ncRecordId" AS nc_record_id,
    ilp."created_at" AS created_at,
    ilp."updated_at" AS updated_at,
    ilp."created_by" AS created_by,
    ilp."updated_by" AS updated_by,
    ilp."nc_order" AS nc_order,
    ii_cold."CoLD_ID" AS instrument_cold_id,
    (COALESCE(ii_cold."CoLD_ID", '') || ' ' || ilp."Provision") AS cold_id
FROM p1q5x3pj29vkrdr."International_Legal_Provisions" ilp
LEFT JOIN LATERAL (
    SELECT ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS "CoLD_ID"
    FROM p1q5x3pj29vkrdr."_nc_m2m_International_I_International_L" miil
    JOIN p1q5x3pj29vkrdr."International_Instruments" ii ON ii.id = miil."International_Instruments_id"
    WHERE miil."International_Legal_Provisions_id" = ilp.id
    ORDER BY ii.id
    LIMIT 1
) ii_cold ON true;

CREATE UNIQUE INDEX idx_international_legal_provisions_complete_id ON data_views.international_legal_provisions_complete(id);
CREATE INDEX idx_international_legal_provisions_complete_cold_id ON data_views.international_legal_provisions_complete(cold_id);
"""

COURT_DECISIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.court_decisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.court_decisions_complete AS
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
    cd."Court's_Position" AS court_s_position,
    cd."Translated_Excerpt" AS translated_excerpt,
    cd."Relevant_Facts" AS relevant_facts,
    cd."Date_of_Judgment" AS date_of_judgment,
    cd."PIL_Provisions" AS pil_provisions,
    cd."Original_Text" AS original_text,
    cd."Quote" AS quote,
    cd."Text_of_the_Relevant_Legal_Provisions" AS text_of_the_relevant_legal_provisions,
    cd."Official_Source__URL_" AS official_source_url,
    cd."Official_Source__PDF_" AS official_source_pdf,
    cd."Answers_Link" AS answers_link,
    cd."Answers_Question" AS answers_question,
    cd."Publication_Date_ISO" AS publication_date_iso,
    cd."Created" AS created,
    cd."ncRecordId" AS nc_record_id,
    cd."created_at" AS created_at,
    cd."updated_at" AS updated_at,
    cd."created_by" AS created_by,
    cd."updated_by" AS updated_by,
    cd."nc_order" AS nc_order,
    jcodes."Alpha_3_Code" AS jurisdictions_alpha_3_code,
    ('CD-' || COALESCE(jcodes."Alpha_3_Code", '') || '-' || cd."ID_Number") AS cold_id,
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
    ORDER BY j.id
    LIMIT 1
) jcodes ON true;

CREATE UNIQUE INDEX idx_court_decisions_complete_id ON data_views.court_decisions_complete(id);
CREATE INDEX idx_court_decisions_complete_cold_id ON data_views.court_decisions_complete(cold_id);
"""

LITERATURE_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.literature_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.literature_complete AS
SELECT
    l.id,
    l."ID_Number" AS id_number,
    l."Key" AS key,
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
    l."Answers" AS answers,
    l."Created" AS created,
    l."ncRecordId" AS nc_record_id,
    l."created_at" AS created_at,
    l."updated_at" AS updated_at,
    l."created_by" AS created_by,
    l."updated_by" AS updated_by,
    l."nc_order" AS nc_order,
    ('L-' || l."ID_Number") AS cold_id,
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
CREATE INDEX idx_literature_complete_cold_id ON data_views.literature_complete(cold_id);
"""

ARBITRAL_AWARDS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_awards_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_awards_complete AS
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
    aa."Created" AS created,
    aa."ncRecordId" AS nc_record_id,
    aa."created_at" AS created_at,
    aa."updated_at" AS updated_at,
    aa."created_by" AS created_by,
    aa."updated_by" AS updated_by,
    aa."nc_order" AS nc_order,
    ('AA-' || aa."ID_Number") AS cold_id,
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
CREATE INDEX idx_arbitral_awards_complete_cold_id ON data_views.arbitral_awards_complete(cold_id);
"""

ARBITRAL_INSTITUTIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_institutions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_institutions_complete AS
SELECT
    ai.id,
    ai."Institution" AS institution,
    ai."Abbreviation" AS abbreviation,
    ai."Created" AS created,
    ai."ncRecordId" AS nc_record_id,
    ai."created_at" AS created_at,
    ai."updated_at" AS updated_at,
    ai."created_by" AS created_by,
    ai."updated_by" AS updated_by,
    ai."nc_order" AS nc_order,
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
"""

ARBITRAL_RULES_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_rules_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_rules_complete AS
SELECT
    ar.id,
    ar."ID_Number" AS id_number,
    ar."Set_of_Rules" AS set_of_rules,
    ar."In_Force_From" AS in_force_from,
    ar."Official_Source__URL_" AS official_source_url,
    ar."Created" AS created,
    ar."ncRecordId" AS nc_record_id,
    ar."created_at" AS created_at,
    ar."updated_at" AS updated_at,
    ar."created_by" AS created_by,
    ar."updated_by" AS updated_by,
    ar."nc_order" AS nc_order,
    ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS cold_id,
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
CREATE INDEX idx_arbitral_rules_complete_cold_id ON data_views.arbitral_rules_complete(cold_id);
"""

ARBITRAL_PROVISIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.arbitral_provisions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.arbitral_provisions_complete AS
SELECT
    ap.id,
    ap."Article" AS article,
    ap."Full_Text_of_the_Provision__Original_Language_" AS full_text_original_language,
    ap."Full_Text_of_the_Provision__English_Translation_" AS full_text_english_translation,
    ap."Arbitration_method_type" AS arbitration_method_type,
    ap."Non_State_law_allowed_in_AoC_" AS non_state_law_allowed_in_aoc,
    ap."Created" AS created,
    ap."ncRecordId" AS nc_record_id,
    ap."created_at" AS created_at,
    ap."updated_at" AS updated_at,
    ap."created_by" AS created_by,
    ap."updated_by" AS updated_by,
    ap."nc_order" AS nc_order,
    ar_cold."CoLD_ID" AS arbitral_rules_cold_id,
    (COALESCE(ar_cold."CoLD_ID", '') || ' ' || COALESCE(ap."Article", '')) AS cold_id,
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
    ORDER BY ar.id
    LIMIT 1
) ar_cold ON true;

CREATE UNIQUE INDEX idx_arbitral_provisions_complete_id ON data_views.arbitral_provisions_complete(id);
CREATE INDEX idx_arbitral_provisions_complete_cold_id ON data_views.arbitral_provisions_complete(cold_id);
"""

JURISDICTIONS_COMPLETE = """
DROP MATERIALIZED VIEW IF EXISTS data_views.jurisdictions_complete CASCADE;
CREATE MATERIALIZED VIEW data_views.jurisdictions_complete AS
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
    j."Answer_Coverage" AS answer_coverage,
    j."Irrelevant_" AS irrelevant,
    j."Done" AS done,
    j."Created" AS created,
    j."ncRecordId" AS nc_record_id,
    j."created_at" AS created_at,
    j."updated_at" AS updated_at,
    j."created_by" AS created_by,
    j."updated_by" AS updated_by,
    j."nc_order" AS nc_order,
    j."Alpha_3_Code" AS cold_id,
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
CREATE INDEX idx_jurisdictions_complete_alpha3 ON data_views.jurisdictions_complete(alpha_3_code);
"""

SEARCH_ALL_FUNCTION = """
DROP FUNCTION IF EXISTS data_views.search_all(text, text[], text[], text[], integer, integer);
DROP FUNCTION IF EXISTS data_views.search_all(text, text[], text[], text[], integer, integer, boolean);

CREATE OR REPLACE FUNCTION data_views.search_all(
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
          AND NOT EXISTS (
              SELECT 1 FROM jsonb_array_elements(a.related_jurisdictions) AS elem
              WHERE COALESCE((elem->>'Irrelevant_')::boolean, FALSE) = TRUE
          )
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

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

SEARCH_FOR_ENTRY_FUNCTION = """
DROP FUNCTION IF EXISTS data_views.search_for_entry(TEXT, TEXT);

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
    IF table_name = 'Answers' THEN
        SELECT id, to_jsonb(a.*),
            jsonb_build_object(
                'related_questions', a.related_questions,
                'related_jurisdictions', a.related_jurisdictions,
                'related_themes', a.related_themes,
                'related_court_decisions', a.related_court_decisions,
                'related_literature', a.related_literature,
                'related_domestic_instruments', a.related_domestic_instruments,
                'related_domestic_legal_provisions', a.related_domestic_legal_provisions
            )
        INTO rec_id, rec, hop1
        FROM data_views.answers_complete a
        WHERE a.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Answers', rec_id, rec, hop1;

    ELSIF table_name = 'HCCH Answers' THEN
        SELECT id, to_jsonb(ha.*),
            jsonb_build_object(
                'related_themes', ha.related_themes,
                'related_international_instruments', ha.related_international_instruments
            )
        INTO rec_id, rec, hop1
        FROM data_views.hcch_answers_complete ha
        WHERE ha.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'HCCH Answers', rec_id, rec, hop1;

    ELSIF table_name = 'Court Decisions' THEN
        SELECT id, to_jsonb(cd.*),
            jsonb_build_object(
                'related_jurisdictions', cd.related_jurisdictions,
                'related_questions', cd.related_questions,
                'related_answers', cd.related_answers,
                'related_themes', cd.related_themes
            )
        INTO rec_id, rec, hop1
        FROM data_views.court_decisions_complete cd
        WHERE cd.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Court Decisions', rec_id, rec, hop1;

    ELSIF table_name = 'Domestic Instruments' THEN
        SELECT id, to_jsonb(di.*),
            jsonb_build_object(
                'related_jurisdictions', di.related_jurisdictions,
                'related_legal_provisions', di.related_legal_provisions,
                'related_questions', di.related_questions
            )
        INTO rec_id, rec, hop1
        FROM data_views.domestic_instruments_complete di
        WHERE di.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Domestic Instruments', rec_id, rec, hop1;

    ELSIF table_name = 'Domestic Legal Provisions' THEN
        SELECT id, to_jsonb(dlp.*),
            jsonb_build_object(
                'related_domestic_instruments', dlp.related_domestic_instruments
            )
        INTO rec_id, rec, hop1
        FROM data_views.domestic_legal_provisions_complete dlp
        WHERE dlp.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Domestic Legal Provisions', rec_id, rec, hop1;

    ELSIF table_name = 'Regional Instruments' THEN
        SELECT id, to_jsonb(ri.*),
            jsonb_build_object(
                'related_specialists', ri.related_specialists,
                'related_legal_provisions', ri.related_legal_provisions
            )
        INTO rec_id, rec, hop1
        FROM data_views.regional_instruments_complete ri
        WHERE ri.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Regional Instruments', rec_id, rec, hop1;

    ELSIF table_name = 'Regional Legal Provisions' THEN
        SELECT id, to_jsonb(rlp.*),
            jsonb_build_object(
                'instrument_cold_id', rlp.instrument_cold_id,
                'related_regional_instruments', rlp.related_regional_instruments
            )
        INTO rec_id, rec, hop1
        FROM data_views.regional_legal_provisions_complete rlp
        WHERE rlp.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Regional Legal Provisions', rec_id, rec, hop1;

    ELSIF table_name = 'International Instruments' THEN
        SELECT id, to_jsonb(ii.*),
            jsonb_build_object(
                'related_specialists', ii.related_specialists,
                'related_hcch_answers', ii.related_hcch_answers,
                'related_legal_provisions', ii.related_legal_provisions,
                'related_literature', ii.related_literature
            )
        INTO rec_id, rec, hop1
        FROM data_views.international_instruments_complete ii
        WHERE ii.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'International Instruments', rec_id, rec, hop1;

    ELSIF table_name = 'International Legal Provisions' THEN
        SELECT id, to_jsonb(ilp.*),
            jsonb_build_object(
                'instrument_cold_id', ilp.instrument_cold_id
            )
        INTO rec_id, rec, hop1
        FROM data_views.international_legal_provisions_complete ilp
        WHERE ilp.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'International Legal Provisions', rec_id, rec, hop1;

    ELSIF table_name = 'Literature' THEN
        SELECT id, to_jsonb(l.*),
            jsonb_build_object(
                'related_jurisdictions', l.related_jurisdictions,
                'related_themes', l.related_themes
            )
        INTO rec_id, rec, hop1
        FROM data_views.literature_complete l
        WHERE l.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Literature', rec_id, rec, hop1;

    ELSIF table_name = 'Arbitral Awards' THEN
        SELECT id, to_jsonb(aa.*),
            jsonb_build_object(
                'related_arbitral_institutions', aa.related_arbitral_institutions,
                'related_arbitral_provisions', aa.related_arbitral_provisions,
                'related_court_decisions', aa.related_court_decisions,
                'related_jurisdictions', aa.related_jurisdictions,
                'related_themes', aa.related_themes
            )
        INTO rec_id, rec, hop1
        FROM data_views.arbitral_awards_complete aa
        WHERE aa.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Awards', rec_id, rec, hop1;

    ELSIF table_name = 'Arbitral Institutions' THEN
        SELECT id, to_jsonb(ai.*),
            jsonb_build_object(
                'related_arbitral_awards', ai.related_arbitral_awards,
                'related_arbitral_rules', ai.related_arbitral_rules,
                'related_arbitral_provisions', ai.related_arbitral_provisions,
                'related_jurisdictions', ai.related_jurisdictions
            )
        INTO rec_id, rec, hop1
        FROM data_views.arbitral_institutions_complete ai
        WHERE ai.id::text = search_for_entry.cold_id
           OR ('AI-' || ai.id::text) = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Institutions', rec_id, rec, hop1;

    ELSIF table_name = 'Arbitral Rules' THEN
        SELECT id, to_jsonb(ar.*),
            jsonb_build_object(
                'related_arbitral_institutions', ar.related_arbitral_institutions,
                'related_arbitral_provisions', ar.related_arbitral_provisions,
                'related_jurisdictions', ar.related_jurisdictions
            )
        INTO rec_id, rec, hop1
        FROM data_views.arbitral_rules_complete ar
        WHERE ar.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Rules', rec_id, rec, hop1;

    ELSIF table_name = 'Arbitral Provisions' THEN
        SELECT id, to_jsonb(ap.*),
            jsonb_build_object(
                'related_arbitral_awards', ap.related_arbitral_awards,
                'related_arbitral_institutions', ap.related_arbitral_institutions,
                'related_arbitral_rules', ap.related_arbitral_rules
            )
        INTO rec_id, rec, hop1
        FROM data_views.arbitral_provisions_complete ap
        WHERE ap.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Arbitral Provisions', rec_id, rec, hop1;

    ELSIF table_name = 'Jurisdictions' THEN
        SELECT id, to_jsonb(j.*),
            jsonb_build_object(
                'related_answers', j.related_answers,
                'related_domestic_instruments', j.related_domestic_instruments,
                'related_court_decisions', j.related_court_decisions,
                'related_literature', j.related_literature,
                'related_specialists', j.related_specialists
            )
        INTO rec_id, rec, hop1
        FROM data_views.jurisdictions_complete j
        WHERE j.alpha_3_code = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Jurisdictions', rec_id, rec, hop1;

    ELSIF table_name = 'Questions' THEN
        SELECT id, to_jsonb(q.*),
            jsonb_build_object(
                'related_themes', q.related_themes,
                'related_answers', q.related_answers,
                'related_court_decisions', q.related_court_decisions,
                'related_domestic_instruments', q.related_domestic_instruments
            )
        INTO rec_id, rec, hop1
        FROM data_views.questions_complete q
        WHERE q.cold_id = search_for_entry.cold_id
        LIMIT 1;

        RETURN QUERY SELECT 'Questions', rec_id, rec, hop1;

    ELSE
        RAISE EXCEPTION 'Unsupported table_name: %', table_name;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
"""

SEARCH_ALL_COUNT_FUNCTION = """
DROP FUNCTION IF EXISTS data_views.search_all_count(text, text[], text[], text[]);

CREATE OR REPLACE FUNCTION data_views.search_all_count(
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
        FROM data_views.answers_complete a
        JOIN data_views.answers search_view ON search_view.id = a.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Answers' = ANY(filter_tables))
          AND NOT EXISTS (
              SELECT 1 FROM jsonb_array_elements(a.related_jurisdictions) AS elem
              WHERE COALESCE((elem->>'Irrelevant_')::boolean, FALSE) = TRUE
          )
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT 1
        FROM data_views.hcch_answers_complete ha
        JOIN data_views.hcch_answers search_view ON search_view.id = ha.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'HCCH Answers' = ANY(filter_tables))
          AND (filter_themes IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_themes) AS tf
               WHERE search_view."Themes" ILIKE '%'||tf||'%'
          ))

        UNION ALL

        SELECT 1
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

        SELECT 1
        FROM data_views.domestic_instruments_complete di
        JOIN data_views.domestic_instruments search_view ON search_view.id = di.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Domestic Instruments' = ANY(filter_tables))
          AND (filter_jurisdictions IS NULL OR EXISTS (
               SELECT 1 FROM unnest(filter_jurisdictions) AS jf
               WHERE search_view."Jurisdictions" ILIKE '%'||jf||'%'
          ))

        UNION ALL

        SELECT 1
        FROM data_views.regional_instruments_complete ri
        JOIN data_views.regional_instruments search_view ON search_view.id = ri.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'Regional Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT 1
        FROM data_views.international_instruments_complete ii
        JOIN data_views.international_instruments search_view ON search_view.id = ii.id
        WHERE (empty_term OR search_view.document @@ plainto_tsquery('english', search_term))
          AND (filter_tables IS NULL OR 'International Instruments' = ANY(filter_tables))

        UNION ALL

        SELECT 1
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
    ) AS sub;

    RETURN total;
END;
$$ LANGUAGE plpgsql STABLE;
"""

REFRESH_FUNCTION = """
CREATE OR REPLACE FUNCTION data_views.refresh_all_materialized_views()
RETURNS void AS $$
DECLARE
    view_name TEXT;
    has_unique_index BOOLEAN;
BEGIN
    FOR view_name IN
        SELECT matviewname FROM pg_matviews WHERE schemaname = 'data_views'
    LOOP
        SELECT EXISTS (
            SELECT 1 FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            JOIN pg_class t ON t.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = 'data_views'
            AND t.relname = view_name
            AND i.indisunique
        ) INTO has_unique_index;

        IF has_unique_index THEN
            EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY data_views.%I', view_name);
        ELSE
            EXECUTE format('REFRESH MATERIALIZED VIEW data_views.%I', view_name);
            RAISE NOTICE 'Materialized view data_views.% refreshed non-concurrently (no unique index)', view_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
"""

REFRESH_VIEWS = """
SELECT data_views.refresh_all_materialized_views();
"""


def upgrade() -> None:
    op.execute(REFRESH_FUNCTION)
    op.execute(QUESTIONS_COMPLETE)
    op.execute(ANSWERS_COMPLETE)
    op.execute(HCCH_ANSWERS_COMPLETE)
    op.execute(DOMESTIC_INSTRUMENTS_COMPLETE)
    op.execute(DOMESTIC_LEGAL_PROVISIONS_COMPLETE)
    op.execute(REGIONAL_INSTRUMENTS_COMPLETE)
    op.execute(REGIONAL_LEGAL_PROVISIONS_COMPLETE)
    op.execute(INTERNATIONAL_INSTRUMENTS_COMPLETE)
    op.execute(INTERNATIONAL_LEGAL_PROVISIONS_COMPLETE)
    op.execute(COURT_DECISIONS_COMPLETE)
    op.execute(LITERATURE_COMPLETE)
    op.execute(ARBITRAL_AWARDS_COMPLETE)
    op.execute(ARBITRAL_INSTITUTIONS_COMPLETE)
    op.execute(ARBITRAL_RULES_COMPLETE)
    op.execute(ARBITRAL_PROVISIONS_COMPLETE)
    op.execute(JURISDICTIONS_COMPLETE)
    op.execute(SEARCH_ALL_COUNT_FUNCTION)
    op.execute(SEARCH_ALL_FUNCTION)
    op.execute(SEARCH_FOR_ENTRY_FUNCTION)
    op.execute(REFRESH_VIEWS)


def downgrade() -> None:
    import importlib

    initial = importlib.import_module("alembic_views.versions.202603071000_initial_views")
    initial.upgrade()
