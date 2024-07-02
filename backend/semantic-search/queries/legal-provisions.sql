-- LEGAL_PROVISIONS TABLE
SELECT
    lp.article,
    lp.original_text,
    lp.english_text,
	COALESCE(STRING_AGG(l.title_english, ', '), 'NA') AS legislation,
    COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
FROM
    legal_provisions lp
LEFT JOIN
	legislationslegal_provisions llp ON lp.legal_provisions_id = llp.legal_provisions_id
LEFT JOIN
	legislations l ON llp.legislations_id = l.legislations_id
LEFT JOIN
    jurisdictionslegal_provisions jlp ON lp.legal_provisions_id = jlp.legal_provisions_id
LEFT JOIN
    jurisdictions j ON jlp.jurisdictions_id = j.jurisdictions_id
GROUP BY
    lp.legal_provisions_id;

-- Legal provisions
-- Everything
-- Double Check for jurisdiction cols / record ID
-- Complementary provisions