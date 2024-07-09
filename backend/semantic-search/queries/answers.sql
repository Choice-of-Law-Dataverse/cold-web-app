--SELECT * FROM tblDLXiRXUqdQKVRm;
SELECT 
    [a].[fields.id],
    [q].[fields.question], 
    [a].[fields.answer], 
    [a].[fields.Open text field], 
    [a].[fields.More information], 
    [j].[fields.Name] AS jurisdiction
FROM 
    tbl3aGDFioDMVFCj1 AS a
JOIN 
    tblDLXiRXUqdQKVRm AS q ON [a].[fields.question] = [q].[fields.Record ID]
JOIN 
    tbl3HFtHN0X1BR2o4 AS j ON [a].[fields.Jurisdiction] = [j].[fields.Record ID];

-- In "{jurisdiction}", the answer to the question "{question}" is "{answer}". {more_information}.

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


