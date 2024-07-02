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