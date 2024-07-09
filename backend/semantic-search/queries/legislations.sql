-- LEGISLATIONS TABLE
SELECT 
    -- l.legislations_id,
    l.[fields.Title (English translation)], 
    l.[fields.Official title],
    l.[fields.Publication date],
    l.[fields.Entry into force],
    --l.type_of_legislation,
    l.[fields.Observations],
    COALESCE(STRING_AGG(j.[fields.Name], ', '), 'NA') AS jurisdiction
FROM 
    tblOAXICRQjFFDUhh l
OUTER APPLY (
	SELECT value AS jurisdictions_id
	FROM STRING_SPLIT([l].[fields.Jurisdictions], ',')
) AS split_jl
LEFT JOIN 
    tbl3HFtHN0X1BR2o4 j ON split_jl.jurisdictions_id = j.ID
GROUP BY
	l.[fields.Title (English translation)], 
    l.[fields.Official title],
    l.[fields.Publication date],
    l.[fields.Entry into force],
    --l.type_of_legislation,
    l.[fields.Observations];


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