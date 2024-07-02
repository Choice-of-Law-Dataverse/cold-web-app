-- COURT_DECISIONS TABLE
SELECT
	cd.court_case,
	cd.abstract,
	cd.relevant_rules_of_law,
	cd.choice_of_law_issue,
	cd.court_position,
	cd.translated_excerpt,
	cd.legal_rules_used_by_court,
	cd.case_content,
	cd.additional_information,
	cd.observations,
	cd.case_quote,
	cd.relevant_facts,
	COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
FROM
	court_decisions cd
LEFT JOIN
	jurisdictionscourt_decisions jcd ON cd.court_decisions_id = jcd.court_decisions_id
LEFT JOIN
	jurisdictions j ON jcd.jurisdictions_id = j.jurisdictions_id
GROUP BY
	cd.court_decisions_id;

-- Court decisions
-- ID
-- Case
-- Jurisdiction name
-- Type (from Jurisdictions) --> not essential for court decisions although it would be nice to have a generic link between jds and their types
-- Answers
-- Link
-- Attachment
-- Abstract
-- cd.relevant_rules_of_law,
-- cd.choice_of_law_issue,
-- cd.court_position,
-- cd.translated_excerpt,
-- cd.legal_rules_used_by_court,
-- cd.case_content,
-- Themes
-- cd.case_quote,
-- cd.relevant_facts,

-- Copyright issues // FOR DISPLAY LOGIC: IF THERE IS AN ISSUE, NO PDF SHOULD BE PROVIDED BUT THE RECORD CAN BE SHOWN
-- cd.additional_information, -- not relevant
-- Judicial hierarchy from Jurisdictions