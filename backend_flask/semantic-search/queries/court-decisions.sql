-- COURT_DECISIONS TABLE
SELECT
    [cd].[fields.Case],
    [cd].[fields.Abstract],
    [cd].[fields.Relevant rules of law involved],
    [cd].[fields.Choice of law issue],
    [cd].[fields.Court's position],
    [cd].[fields.Translated excerpt],
    [cd].[fields.Text of the relevant legal provisions],
    [cd].[fields.Content],
    [cd].[fields.Additional information],
    [cd].[fields.Observations],
    [cd].[fields.Quote],
    [cd].[fields.Relevant facts],
    COALESCE(STRING_AGG([j].[fields.Name], ', '), 'NA') AS jurisdictions
FROM
    tbl8hWTY8ArXzJCr2 cd
OUTER APPLY (
    SELECT value AS jurisdictions_id
    FROM STRING_SPLIT([cd].[fields.Jurisdictions], ',')
) AS split_jcd
LEFT JOIN
    tbl3HFtHN0X1BR2o4 j ON split_jcd.[jurisdictions_id] = [j].[ID]
-- WHERE
    -- [cd].[fields.Case] = 'Bundesgerichtshof, BGH (Federal Supreme Court of Justice), 29 November 2023, VIII ZR 7/23'
GROUP BY
    [cd].[ID],
    [cd].[fields.Case],
    [cd].[fields.Abstract],
    [cd].[fields.Relevant rules of law involved],
    [cd].[fields.Choice of law issue],
    [cd].[fields.Court's position],
    [cd].[fields.Translated excerpt],
    [cd].[fields.Text of the relevant legal provisions],
    [cd].[fields.Content],
    [cd].[fields.Additional information],
    [cd].[fields.Observations],
    [cd].[fields.Quote],
    [cd].[fields.Relevant facts];

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