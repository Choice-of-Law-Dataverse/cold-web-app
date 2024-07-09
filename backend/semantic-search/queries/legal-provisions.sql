-- LEGAL_PROVISIONS TABLE
SELECT
    lp.[fields.Article],
    lp.[fields.Full text of the provision (Original language)],
    lp.[fields.Full text of the provision (English translation)],
	COALESCE(STRING_AGG(l.[fields.Title (English translation)], ', '), 'NA') AS legislation,
    COALESCE(STRING_AGG(j.[fields.Name], ', '), 'NA') AS jurisdiction
FROM
    tbl9T17hyxLey2LG1 lp
OUTER APPLY (
	SELECT value AS legislations_id
	FROM STRING_SPLIT([lp].[fields.Corresponding legislation], ',')
) AS split_llp
LEFT JOIN
	tblOAXICRQjFFDUhh l ON split_llp.legislations_id = l.ID
OUTER APPLY (
	SELECT value as jurisdictions_id
	FROM STRING_SPLIT([lp].[fields.Jurisdictions], ',')
) AS split_jlp
LEFT JOIN
    tbl3HFtHN0X1BR2o4 j ON split_jlp.jurisdictions_id = j.ID
GROUP BY
    lp.ID,
	lp.[fields.Article],
    lp.[fields.Full text of the provision (Original language)],
    lp.[fields.Full text of the provision (English translation)];

-- Legal provisions
-- Everything
-- Double Check for jurisdiction cols / record ID
-- Complementary provisions