from __future__ import annotations

from alembic import op

revision = "202603111000"
down_revision = "202603091000"
branch_labels = None
depends_on = None

SCHEMA = "p1q5x3pj29vkrdr"
S = SCHEMA

DETAIL_FUNCTION = f"""
DROP FUNCTION IF EXISTS data_views.get_entity_detail(TEXT, TEXT);

CREATE OR REPLACE FUNCTION data_views.get_entity_detail(
    p_table_name TEXT,
    p_cold_id TEXT
)
RETURNS TABLE (
    source_table TEXT,
    record_id INTEGER,
    cold_id TEXT,
    base_record JSONB,
    relations JSONB
) AS $$
DECLARE
    v_id INTEGER;
    v_cold_id TEXT;
    v_base JSONB;
    v_rels JSONB;
BEGIN
    IF p_table_name = 'Answers' THEN
        SELECT a.id,
            ac.cold_id,
            jsonb_build_object(
                'answer', a."Answer",
                'more_information', a."More_Information",
                'to_review', a."To_Review_",
                'oup_book_quote', a."OUP_Book_Quote",
                'jurisdictions_alpha_3_code', jcodes."Alpha_3_Code",
                'question_cold_id', qcold.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Answers" a
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM {S}."_nc_m2m_Jurisdictions_Answers" ja
            JOIN {S}."Jurisdictions" j ON j.id = ja."Jurisdictions_id"
            WHERE ja."Answers_id" = a.id ORDER BY j.id LIMIT 1
        ) jcodes ON true
        LEFT JOIN LATERAL (
            SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS cold_id
            FROM {S}."_nc_m2m_Questions_Answers" qa
            JOIN {S}."Questions" q ON q.id = qa."Questions_id"
            WHERE qa."Answers_id" = a.id ORDER BY q.id LIMIT 1
        ) qcold ON true
        LEFT JOIN data_views.rel_answers ac ON ac.id = a.id
        WHERE ac.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Answers" m ON m."Questions_id" = r.id
                WHERE m."Answers_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Answers" m ON m."Jurisdictions_id" = r.id
                WHERE m."Answers_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(DISTINCT to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Themes_id" = r.id
                JOIN {S}."_nc_m2m_Questions_Answers" qa ON qa."Questions_id" = tq."Questions_id"
                WHERE qa."Answers_id" = v_id
            ), '[]'::jsonb),
            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Answers_Court_Decisions" m ON m."Court_Decisions_id" = r.id
                WHERE m."Answers_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_Answers_Literature" m ON m."Literature_id" = r.id
                WHERE m."Answers_id" = v_id
            ), '[]'::jsonb),
            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                JOIN {S}."_nc_m2m_Answers_Domestic_Instru" m ON m."Domestic_Instruments_id" = r.id
                WHERE m."Answers_id" = v_id
            ), '[]'::jsonb),
            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                WHERE r.id IN (
                    SELECT m."Domestic_Legal_Provisions_id" FROM {S}."_nc_m2m_Answers_Domestic_Legal_" m WHERE m."Answers_id" = v_id
                    UNION
                    SELECT m."Domestic_Legal_Provisions_id" FROM {S}."_nc_m2m_Answers_Domestic_Legal_1" m WHERE m."Answers_id" = v_id
                )
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Answers'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'HCCH Answers' THEN
        SELECT ha.id,
            hac.cold_id,
            jsonb_build_object(
                'adapted_question', ha."Adapted_Question",
                'position', ha."Position",
                'question_cold_id', qcold.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."HCCH_Answers" ha
        LEFT JOIN LATERAL (
            SELECT (q."Question_Number" || '-' || q."Primary_Theme") AS cold_id
            FROM {S}."_nc_m2m_Questions_HCCH_Answers" qa
            JOIN {S}."Questions" q ON q.id = qa."Questions_id"
            WHERE qa."HCCH_Answers_id" = ha.id ORDER BY q.id LIMIT 1
        ) qcold ON true
        LEFT JOIN data_views.rel_hcch_answers hac ON hac.id = ha.id
        WHERE hac.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_HCCH_Answers" m ON m."Themes_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'international_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_instruments r
                JOIN {S}."_nc_m2m_HCCH_Answers_International_I" m ON m."International_Instruments_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                JOIN {S}."_nc_m2m_HCCH_Answers_International_L" m ON m."International_Legal_Provisions_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'regional_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_instruments r
                JOIN {S}."_nc_m2m_HCCH_Answers_Regional_Instru" m ON m."Regional_Instruments_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                JOIN {S}."_nc_m2m_HCCH_Answers_Regional_Legal_" m ON m."Regional_Legal_Provisions_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_HCCH_Answers" m ON m."Questions_id" = r.id
                WHERE m."HCCH_Answers_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'HCCH Answers'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Questions' THEN
        SELECT q.id,
            (q."Question_Number" || '-' || q."Primary_Theme"),
            jsonb_build_object(
                'question', q."Question",
                'question_number', q."Question_Number",
                'primary_theme', q."Primary_Theme",
                'answering_options', q."Answering_Options"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Questions" q
        WHERE (q."Question_Number" || '-' || q."Primary_Theme") = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Questions" m ON m."Themes_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" m ON m."Court_Decisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                JOIN {S}."_nc_m2m_Questions_Domestic_Instru" m ON m."Domestic_Instruments_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_hcch_answers r
                JOIN {S}."_nc_m2m_Questions_HCCH_Answers" m ON m."HCCH_Answers_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Legal_" m ON m."Domestic_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_International_L" m ON m."International_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                JOIN {S}."_nc_m2m_Questions_Regional_Legal_" m ON m."Regional_Legal_Provisions_id" = r.id
                WHERE m."Questions_id" = v_id
            ), '[]'::jsonb),
            'questions', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Questions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Court Decisions' THEN
        SELECT cd.id,
            cdc.cold_id,
            jsonb_build_object(
                'id_number', cd."ID_Number",
                'case_citation', cd."Case_Citation",
                'case_title', cd."Case_Title",
                'instance', cd."Instance",
                'date', cd."Date",
                'abstract', cd."Abstract",
                'case_rank', cd."Case_Rank",
                'english_translation', cd."English_Translation",
                'choice_of_law_issue', cd."Choice_of_Law_Issue",
                'court_s_position', cd."Court_s_Position",
                'translated_excerpt', cd."Translated_Excerpt",
                'relevant_facts', cd."Relevant_Facts",
                'date_of_judgment', cd."Date_of_Judgment",
                'pil_provisions', cd."PIL_Provisions",
                'original_text', cd."Original_Text",
                'quote', cd."Quote",
                'text_of_the_relevant_legal_provisions', cd."Text_of_the_Relevant_Legal_Provisions",
                'official_source_url', cd."Official_Source__URL_",
                'official_source_pdf', cd."Official_Source__PDF_",
                'publication_date_iso', cd."Publication_Date_ISO",
                'jurisdictions_alpha_3_code', jcodes."Alpha_3_Code"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Court_Decisions" cd
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM {S}."_nc_m2m_Jurisdictions_Court_Decisions" jcd
            JOIN {S}."Jurisdictions" j ON j.id = jcd."Jurisdictions_id"
            WHERE jcd."Court_Decisions_id" = cd.id ORDER BY j.id LIMIT 1
        ) jcodes ON true
        LEFT JOIN data_views.rel_court_decisions cdc ON cdc.id = cd.id
        WHERE cdc.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Court_Decisions" m ON m."Jurisdictions_id" = r.id
                WHERE m."Court_Decisions_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" m ON m."Questions_id" = r.id
                WHERE m."Court_Decisions_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(DISTINCT to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Questions" tq ON tq."Themes_id" = r.id
                JOIN {S}."_nc_m2m_Questions_Court_Decisions" qcd ON qcd."Questions_id" = tq."Questions_id"
                WHERE qcd."Court_Decisions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_awards', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_awards r
                JOIN {S}."_nc_m2m_Court_Decisions_Arbitral_Awards" m ON m."Arbitral_Awards_id" = r.id
                WHERE m."Court_Decisions_id" = v_id
            ), '[]'::jsonb),
            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                JOIN {S}."_nc_m2m_Domestic_Legal__Court_Decisions" m ON m."Domestic_Legal_Provisions_id" = r.id
                WHERE m."Court_Decisions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Court Decisions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Domestic Instruments' THEN
        SELECT di.id,
            dic.cold_id,
            jsonb_build_object(
                'id_number', di."ID_Number",
                'title_in_english', di."Title__in_English_",
                'official_title', di."Official_Title",
                'date', di."Date",
                'status', di."Status",
                'abbreviation', di."Abbreviation",
                'relevant_provisions', di."Relevant_Provisions",
                'full_text_of_the_provisions', di."Full_Text_of_the_Provisions",
                'publication_date', di."Publication_Date",
                'entry_into_force', di."Entry_Into_Force",
                'source_url', di."Source__URL_",
                'source_pdf', di."Source__PDF_",
                'compatible_with_the_hcch_principles', di."Compatible_With_the_HCCH_Principles_",
                'compatible_with_the_uncitral_model_law', di."Compatible_With_the_UNCITRAL_Model_Law_",
                'jurisdictions_alpha_3_code', jcodes."Alpha_3_Code"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Domestic_Instruments" di
        LEFT JOIN LATERAL (
            SELECT j."Alpha_3_Code"
            FROM {S}."_nc_m2m_Jurisdictions_Domestic_Instru" jdi
            JOIN {S}."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
            WHERE jdi."Domestic_Instruments_id" = di.id ORDER BY j.id LIMIT 1
        ) jcodes ON true
        LEFT JOIN data_views.rel_domestic_instruments dic ON dic.id = di.id
        WHERE dic.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Domestic_Instru" m ON m."Jurisdictions_id" = r.id
                WHERE m."Domestic_Instruments_id" = v_id
            ), '[]'::jsonb),
            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                JOIN {S}."_nc_m2m_Domestic_Instru_Domestic_Legal_" m ON m."Domestic_Legal_Provisions_id" = r.id
                WHERE m."Domestic_Instruments_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Instru" m ON m."Questions_id" = r.id
                WHERE m."Domestic_Instruments_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Domestic_Instru_Themes" m ON m."Themes_id" = r.id
                WHERE m."Domestic_Instruments_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Domestic Instruments'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Domestic Legal Provisions' THEN
        SELECT dlp.id,
            dlpc.cold_id,
            jsonb_build_object(
                'article', dlp."Article",
                'full_text_of_the_provision_original_language', dlp."Full_Text_of_the_Provision__Original_Language_",
                'full_text_of_the_provision_english_translation', dlp."Full_Text_of_the_Provision__English_Translation_",
                'ranking_display_order', dlp."Ranking__Display_Order_",
                'domestic_instrument_cold_id', di_lat.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Domestic_Legal_Provisions" dlp
        LEFT JOIN LATERAL (
            SELECT ('DI-' || COALESCE(j."Alpha_3_Code", '') || '-' || di."ID_Number") AS cold_id
            FROM {S}."_nc_m2m_Domestic_Instru_Domestic_Legal_" didlp
            JOIN {S}."Domestic_Instruments" di ON di.id = didlp."Domestic_Instruments_id"
            LEFT JOIN {S}."_nc_m2m_Jurisdictions_Domestic_Instru" jdi ON jdi."Domestic_Instruments_id" = di.id
            LEFT JOIN {S}."Jurisdictions" j ON j.id = jdi."Jurisdictions_id"
            WHERE didlp."Domestic_Legal_Provisions_id" = dlp.id ORDER BY di.id LIMIT 1
        ) di_lat ON true
        LEFT JOIN data_views.rel_domestic_legal_provisions dlpc ON dlpc.id = dlp.id
        WHERE dlpc.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                JOIN {S}."_nc_m2m_Domestic_Instru_Domestic_Legal_" m ON m."Domestic_Instruments_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Domestic_Legal__Court_Decisions" m ON m."Court_Decisions_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Domestic_Legal_" m ON m."Jurisdictions_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Domestic_Legal_" m ON m."Questions_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Domestic_Legal_" m ON m."Themes_id" = r.id
                WHERE m."Domestic_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Domestic Legal Provisions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Regional Instruments' THEN
        SELECT ri.id,
            ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number"),
            jsonb_build_object(
                'id_number', ri."ID_Number",
                'title', ri."Title",
                'abbreviation', ri."Abbreviation",
                'date', ri."Date",
                'url', ri."URL",
                'attachment', ri."Attachment"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Regional_Instruments" ri
        WHERE ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'specialists', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_specialists r
                JOIN {S}."_nc_m2m_Regional_Instru_Specialists" m ON m."Specialists_id" = r.id
                WHERE m."Regional_Instruments_id" = v_id
            ), '[]'::jsonb),
            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                JOIN {S}."_nc_m2m_Regional_Instru_Regional_Legal_" m ON m."Regional_Legal_Provisions_id" = r.id
                WHERE m."Regional_Instruments_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_hcch_answers r
                JOIN {S}."_nc_m2m_HCCH_Answers_Regional_Instru" m ON m."HCCH_Answers_id" = r.id
                WHERE m."Regional_Instruments_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_Regional_Instru_Literature" m ON m."Literature_id" = r.id
                WHERE m."Regional_Instruments_id" = v_id
            ), '[]'::jsonb),
            'questions', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Regional Instruments'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Regional Legal Provisions' THEN
        SELECT rlp.id,
            rlpc.cold_id,
            jsonb_build_object(
                'provision', rlp."Provision",
                'title_of_the_provision', rlp."Title_of_the_Provision",
                'full_text', rlp."Full_Text",
                'instrument_cold_id', ri_lat.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Regional_Legal_Provisions" rlp
        LEFT JOIN LATERAL (
            SELECT ('RI-' || LEFT(ri."Abbreviation", 3) || '-' || ri."ID_Number") AS cold_id
            FROM {S}."_nc_m2m_Regional_Instru_Regional_Legal_" mirl
            JOIN {S}."Regional_Instruments" ri ON ri.id = mirl."Regional_Instruments_id"
            WHERE mirl."Regional_Legal_Provisions_id" = rlp.id ORDER BY ri.id LIMIT 1
        ) ri_lat ON true
        LEFT JOIN data_views.rel_regional_legal_provisions rlpc ON rlpc.id = rlp.id
        WHERE rlpc.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'regional_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_instruments r
                JOIN {S}."_nc_m2m_Regional_Instru_Regional_Legal_" m ON m."Regional_Instruments_id" = r.id
                WHERE m."Regional_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_hcch_answers r
                JOIN {S}."_nc_m2m_HCCH_Answers_Regional_Legal_" m ON m."HCCH_Answers_id" = r.id
                WHERE m."Regional_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_Regional_Legal_" m ON m."Questions_id" = r.id
                WHERE m."Regional_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_Regional_Legal__Literature" m ON m."Literature_id" = r.id
                WHERE m."Regional_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Regional Legal Provisions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'International Instruments' THEN
        SELECT ii.id,
            ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number"),
            jsonb_build_object(
                'id_number', ii."ID_Number",
                'name', ii."Name",
                'date', ii."Date",
                'url', ii."URL",
                'attachment', ii."Attachment"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."International_Instruments" ii
        WHERE ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'specialists', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_specialists r
                JOIN {S}."_nc_m2m_International_I_Specialists" m ON m."Specialists_id" = r.id
                WHERE m."International_Instruments_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_hcch_answers r
                JOIN {S}."_nc_m2m_HCCH_Answers_International_I" m ON m."HCCH_Answers_id" = r.id
                WHERE m."International_Instruments_id" = v_id
            ), '[]'::jsonb),
            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                JOIN {S}."_nc_m2m_International_I_International_L" m ON m."International_Legal_Provisions_id" = r.id
                WHERE m."International_Instruments_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_International_I_Literature" m ON m."Literature_id" = r.id
                WHERE m."International_Instruments_id" = v_id
            ), '[]'::jsonb),
            'questions', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'International Instruments'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'International Legal Provisions' THEN
        SELECT ilp.id,
            ilpc.cold_id,
            jsonb_build_object(
                'provision', ilp."Provision",
                'title_of_the_provision', ilp."Title_of_the_Provision",
                'full_text', ilp."Full_Text",
                'ranking_display_order', ilp."Ranking__Display_Order_",
                'instrument_cold_id', ii_lat.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."International_Legal_Provisions" ilp
        LEFT JOIN LATERAL (
            SELECT ('II-' || LEFT(ii."Name", 3) || '-' || ii."ID_Number") AS cold_id
            FROM {S}."_nc_m2m_International_I_International_L" miil
            JOIN {S}."International_Instruments" ii ON ii.id = miil."International_Instruments_id"
            WHERE miil."International_Legal_Provisions_id" = ilp.id ORDER BY ii.id LIMIT 1
        ) ii_lat ON true
        LEFT JOIN data_views.rel_international_legal_provisions ilpc ON ilpc.id = ilp.id
        WHERE ilpc.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'international_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_instruments r
                JOIN {S}."_nc_m2m_International_I_International_L" m ON m."International_Instruments_id" = r.id
                WHERE m."International_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_hcch_answers r
                JOIN {S}."_nc_m2m_HCCH_Answers_International_L" m ON m."HCCH_Answers_id" = r.id
                WHERE m."International_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'questions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_questions r
                JOIN {S}."_nc_m2m_Questions_International_L" m ON m."Questions_id" = r.id
                WHERE m."International_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_International_L_Literature" m ON m."Literature_id" = r.id
                WHERE m."International_Legal_Provisions_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'International Legal Provisions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Literature' THEN
        SELECT l.id,
            ('L-' || l."ID_Number"),
            jsonb_build_object(
                'id_number', l."ID_Number",
                'item_type', l."Item_Type",
                'publication_year', l."Publication_Year",
                'author', l."Author",
                'title', l."Title",
                'publication_title', l."Publication_Title",
                'abstract_note', l."Abstract_Note",
                'isbn', l."ISBN",
                'issn', l."ISSN",
                'doi', l."DOI",
                'url', l."Url",
                'date', l."Date",
                'date_added', l."Date_Added",
                'date_modified', l."Date_Modified",
                'publisher', l."Publisher",
                'language', l."Language",
                'extra', l."Extra",
                'manual_tags', l."Manual_Tags",
                'editor', l."Editor",
                'issue', l."Issue",
                'volume', l."Volume",
                'pages', l."Pages",
                'library_catalog', l."Library_Catalog",
                'access_date', l."Access_Date",
                'open_access', l."Open_Access",
                'open_access_url', l."Open_Access_URL",
                'journal_abbreviation', l."Journal_Abbreviation",
                'short_title', l."Short_Title",
                'place', l."Place",
                'num_pages', l."Num_Pages",
                'type', l."Type",
                'oup_jd_chapter', l."OUP_JD_Chapter",
                'contributor', l."Contributor",
                'automatic_tags', l."Automatic_Tags",
                'number', l."Number",
                'series', l."Series",
                'series_number', l."Series_Number",
                'series_editor', l."Series_Editor",
                'edition', l."Edition",
                'call_number', l."Call_Number",
                'jurisdiction_summary', l."Jurisdiction_Summary"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Literature" l
        WHERE ('L-' || l."ID_Number") = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Literature" m ON m."Jurisdictions_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Literature" m ON m."Themes_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'international_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_instruments r
                JOIN {S}."_nc_m2m_International_I_Literature" m ON m."International_Instruments_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'international_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_legal_provisions r
                JOIN {S}."_nc_m2m_International_L_Literature" m ON m."International_Legal_Provisions_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'regional_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_instruments r
                JOIN {S}."_nc_m2m_Regional_Instru_Literature" m ON m."Regional_Instruments_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'regional_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_legal_provisions r
                JOIN {S}."_nc_m2m_Regional_Legal__Literature" m ON m."Regional_Legal_Provisions_id" = r.id
                WHERE m."Literature_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Literature'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Arbitral Awards' THEN
        SELECT aa.id,
            ('AA-' || aa."ID_Number"),
            jsonb_build_object(
                'id_number', aa."ID_Number",
                'case_number', aa."Case_Number",
                'context', aa."Context",
                'award_summary', aa."Award_Summary",
                'year', aa."Year",
                'nature_of_the_award', aa."Nature_of_the_Award",
                'seat_town', aa."Seat__Town_",
                'source', aa."Source"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Arbitral_Awards" aa
        WHERE ('AA-' || aa."ID_Number") = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'arbitral_institutions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_institutions r
                JOIN {S}."_nc_m2m_Arbitral_Instit_Arbitral_Awards" m ON m."Arbitral_Institutions_id" = r.id
                WHERE m."Arbitral_Awards_id" = v_id
            ), '[]'::jsonb),
            'arbitral_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_provisions r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Awards" m ON m."Arbitral Provisions_id" = r.id
                WHERE m."Arbitral_Awards_id" = v_id
            ), '[]'::jsonb),
            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Court_Decisions_Arbitral_Awards" m ON m."Court_Decisions_id" = r.id
                WHERE m."Arbitral_Awards_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Arbitral_Awards" m ON m."Jurisdictions_id" = r.id
                WHERE m."Arbitral_Awards_id" = v_id
            ), '[]'::jsonb),
            'themes', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_themes r
                JOIN {S}."_nc_m2m_Themes_Arbitral_Awards" m ON m."Themes_id" = r.id
                WHERE m."Arbitral_Awards_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Arbitral Awards'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Arbitral Institutions' THEN
        SELECT ai.id,
            ('AI-' || ai.id),
            jsonb_build_object(
                'institution', ai."Institution",
                'abbreviation', ai."Abbreviation"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Arbitral_Institutions" ai
        WHERE ai.id::text = p_cold_id
           OR ('AI-' || ai.id::text) = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'arbitral_awards', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_awards r
                JOIN {S}."_nc_m2m_Arbitral_Instit_Arbitral_Awards" m ON m."Arbitral_Awards_id" = r.id
                WHERE m."Arbitral_Institutions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_rules', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_rules r
                JOIN {S}."_nc_m2m_Arbitral_Instit_Arbitral_Rules" m ON m."Arbitral_Rules_id" = r.id
                WHERE m."Arbitral_Institutions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_provisions r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Instit" m ON m."Arbitral Provisions_id" = r.id
                WHERE m."Arbitral_Institutions_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Arbitral_Instit" m ON m."Jurisdictions_id" = r.id
                WHERE m."Arbitral_Institutions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Arbitral Institutions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Arbitral Rules' THEN
        SELECT ar.id,
            ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)),
            jsonb_build_object(
                'id_number', ar."ID_Number",
                'set_of_rules', ar."Set_of_Rules",
                'in_force_from', ar."In_Force_From",
                'official_source_url', ar."Official_Source__URL_"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Arbitral_Rules" ar
        WHERE ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'arbitral_institutions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_institutions r
                JOIN {S}."_nc_m2m_Arbitral_Instit_Arbitral_Rules" m ON m."Arbitral_Institutions_id" = r.id
                WHERE m."Arbitral_Rules_id" = v_id
            ), '[]'::jsonb),
            'arbitral_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_provisions r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Rules" m ON m."Arbitral Provisions_id" = r.id
                WHERE m."Arbitral_Rules_id" = v_id
            ), '[]'::jsonb),
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(DISTINCT to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Arbitral_Instit" jai ON jai."Jurisdictions_id" = r.id
                JOIN {S}."_nc_m2m_Arbitral_Instit_Arbitral_Rules" air ON air."Arbitral_Institutions_id" = jai."Arbitral_Institutions_id"
                WHERE air."Arbitral_Rules_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Arbitral Rules'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Arbitral Provisions' THEN
        SELECT ap.id,
            apc.cold_id,
            jsonb_build_object(
                'article', ap."Article",
                'full_text_original_language', ap."Full_Text_of_the_Provision__Original_Language_",
                'full_text_english_translation', ap."Full_Text_of_the_Provision__English_Translation_",
                'arbitration_method_type', ap."Arbitration_method_type",
                'non_state_law_allowed_in_aoc', ap."Non_State_law_allowed_in_AoC_",
                'arbitral_rules_cold_id', ar_lat.cold_id
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Arbitral Provisions" ap
        LEFT JOIN LATERAL (
            SELECT ('AR-' || COALESCE(ar."ID_Number"::text, ar.id::text)) AS cold_id
            FROM {S}."_nc_m2m_Arbitral Provis_Arbitral_Rules" m
            JOIN {S}."Arbitral_Rules" ar ON ar.id = m."Arbitral_Rules_id"
            WHERE m."Arbitral Provisions_id" = ap.id ORDER BY ar.id LIMIT 1
        ) ar_lat ON true
        LEFT JOIN data_views.rel_arbitral_provisions apc ON apc.id = ap.id
        WHERE apc.cold_id = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'arbitral_awards', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_awards r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Awards" m ON m."Arbitral_Awards_id" = r.id
                WHERE m."Arbitral Provisions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_institutions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_institutions r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Instit" m ON m."Arbitral_Institutions_id" = r.id
                WHERE m."Arbitral Provisions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_rules', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_rules r
                JOIN {S}."_nc_m2m_Arbitral Provis_Arbitral_Rules" m ON m."Arbitral_Rules_id" = r.id
                WHERE m."Arbitral Provisions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Arbitral Provisions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Jurisdictions' THEN
        SELECT j.id,
            j."Alpha_3_Code",
            jsonb_build_object(
                'name', j."Name",
                'type', j."Type",
                'region', j."Region",
                'north_south_divide', j."North_South_Divide",
                'jurisdictional_differentiator', j."Jurisdictional_Differentiator",
                'legal_family', j."Legal_Family",
                'jurisdiction_summary', j."Jurisdiction_Summary",
                'irrelevant', j."Irrelevant_",
                'done', j."Done"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Jurisdictions" j
        WHERE j."Alpha_3_Code" = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'domestic_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_instruments r
                JOIN {S}."_nc_m2m_Jurisdictions_Domestic_Instru" m ON m."Domestic_Instruments_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'court_decisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_court_decisions r
                JOIN {S}."_nc_m2m_Jurisdictions_Court_Decisions" m ON m."Court_Decisions_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'literature', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_literature r
                JOIN {S}."_nc_m2m_Jurisdictions_Literature" m ON m."Literature_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'specialists', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_specialists r
                JOIN {S}."_nc_m2m_Jurisdictions_Specialists" m ON m."Specialists_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_awards', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_awards r
                JOIN {S}."_nc_m2m_Jurisdictions_Arbitral_Awards" m ON m."Arbitral_Awards_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'arbitral_institutions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_arbitral_institutions r
                JOIN {S}."_nc_m2m_Jurisdictions_Arbitral_Instit" m ON m."Arbitral_Institutions_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'domestic_legal_provisions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_domestic_legal_provisions r
                JOIN {S}."_nc_m2m_Jurisdictions_Domestic_Legal_" m ON m."Domestic_Legal_Provisions_id" = r.id
                WHERE m."Jurisdictions_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'jurisdictions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'regional_instruments', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_instruments', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Jurisdictions'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSIF p_table_name = 'Specialists' THEN
        SELECT s.id,
            ('SP-' || s.id),
            jsonb_build_object(
                'specialist', s."Specialist",
                'affiliation', s."Affiliation",
                'contact', s."Contact",
                'bio', s."Bio",
                'website', s."Website"
            )
        INTO v_id, v_cold_id, v_base
        FROM {S}."Specialists" s
        WHERE s.id::text = p_cold_id
           OR ('SP-' || s.id::text) = p_cold_id
        LIMIT 1;

        SELECT jsonb_build_object(
            'jurisdictions', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_jurisdictions r
                JOIN {S}."_nc_m2m_Jurisdictions_Specialists" m ON m."Jurisdictions_id" = r.id
                WHERE m."Specialists_id" = v_id
            ), '[]'::jsonb),
            'international_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_international_instruments r
                JOIN {S}."_nc_m2m_International_I_Specialists" m ON m."International_Instruments_id" = r.id
                WHERE m."Specialists_id" = v_id
            ), '[]'::jsonb),
            'regional_instruments', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.rel_regional_instruments r
                JOIN {S}."_nc_m2m_Regional_Instru_Specialists" m ON m."Regional_Instruments_id" = r.id
                WHERE m."Specialists_id" = v_id
            ), '[]'::jsonb),
            'hcch_answers', '[]'::jsonb,
            'questions', '[]'::jsonb,
            'themes', '[]'::jsonb,
            'court_decisions', '[]'::jsonb,
            'literature', '[]'::jsonb,
            'domestic_instruments', '[]'::jsonb,
            'domestic_legal_provisions', '[]'::jsonb,
            'regional_legal_provisions', '[]'::jsonb,
            'international_legal_provisions', '[]'::jsonb,
            'arbitral_awards', '[]'::jsonb,
            'arbitral_institutions', '[]'::jsonb,
            'arbitral_rules', '[]'::jsonb,
            'arbitral_provisions', '[]'::jsonb,
            'specialists', '[]'::jsonb
        ) INTO v_rels;

        RETURN QUERY SELECT 'Specialists'::TEXT, v_id, v_cold_id, v_base, v_rels;

    ELSE
        RAISE EXCEPTION 'Unsupported table_name: %', p_table_name;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
"""


def upgrade() -> None:
    op.execute(DETAIL_FUNCTION)


def downgrade() -> None:
    pass
