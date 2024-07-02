SELECT 
    a.id,
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
    jurisdictions j ON a.jurisdiction = j.record_id
JOIN
    ;
	
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


