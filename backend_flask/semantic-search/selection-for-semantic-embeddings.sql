-- SQL QUERIES FOR VECTOR EMBEDDINGS


-- ANSWERS TABLE
SELECT 
    q.question, 
    a.answer, 
    a.open_text_field, 
    a.more_information, 
    j.jd_name AS jurisdiction
FROM 
    answers a
JOIN 
    questions q ON a.question = q.record_id
JOIN 
    jurisdictions j ON a.jurisdiction = j.record_id;
	

-- QUESTIONS TABLE
SELECT
	question,
	themes
FROM
	questions;


-- JURISDICTIONS TABLE
SELECT
	jurisdictions_id,
	jd_name,
	jd_type,
	region,
	north_south_divide
FROM
	jurisdictions;


-- LEGISLATIONS TABLE
-- NOTE THAT POR-30 MISSES A VALUE FOR ITS JD, SO NEEDS TO BE UPDATED VIA AIRTABLE! (THE FOLLOWING CODE RETRIEVES ONE LESS ROW THAN ACTUALLY PRESENT IN LEGISLATIONS)
SELECT 
    -- l.legislations_id,
    l.title_english, 
    l.title_official,
    l.publication_date,
    l.entry_into_force,
    l.type_of_legislation,
    l.observations,
    COALESCE(STRING_AGG(j.jd_name, ', '), 'NA') AS jurisdiction
FROM 
    legislations l
LEFT JOIN 
    jurisdictionslegislations jl ON l.legislations_id = jl.legislations_id
LEFT JOIN 
    jurisdictions j ON jl.jurisdictions_id = j.jurisdictions_id
GROUP BY 
    l.legislations_id;
-- ORDER BY l.legislations_id ASC;


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




-- TABLES AND THEIR RELEVANT COLUMNS

-- Answers
-- What is the French legal framework for Choice of Law? --> Filter by Jurisdiction as first instance
-- ID
-- Questions
-- Jurisdiction name
-- Answer
-- More information
-- Legal provisions
-- Secondary Legal Provisions
-- Legislation
-- Cases
-- Themes (from Question)


-- Questions
-- Irrelevant for data search


-- Jurisdictions
-- Irrelevant for data search


-- Legislation
-- When were the HCCH Principles adopted in Mozambique?
-- ID
-- Title (English translation)
-- Official title
-- Publication date
-- Entry into force
-- Jurisdiction name
-- Type (from Jurisdiction)
-- Answers
-- Relevant Privisions // AS LONG AS DATA IN THERE, KEEP
-- Full text of the provisions // AS LONG AS DATA IN THERE, KEEP
-- Type of legislation
-- Official Source (URL)
-- Official Source (PDF)
-- Legal provisions


-- Legal provisions
-- Everything
-- Double Check for jurisdiction cols / record ID
-- Complementary provisions


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



-- Concepts
-- Concept
-- Definition
