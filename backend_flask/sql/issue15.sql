-- COMBINED SEARCH

-- Search in "Answers", "Court decisions", and "Legislation" tables with the same query

-- Search in "Answers" table
select 
    'Answers' as source_table,               -- Column to indicate the source table
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'party autonomy')) +
    ts_rank(search, websearch_to_tsquery('simple', 'party autonomy')) as rank
from "Answers"
where search @@ websearch_to_tsquery('english', 'party autonomy')
    or search @@ websearch_to_tsquery('simple', 'party autonomy')

union all

-- Search in "Court decisions" table
select 
    'Court decisions' as source_table,       -- Indicate the source table
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'party autonomy')) +
    ts_rank(search, websearch_to_tsquery('simple', 'party autonomy')) as rank
from "Court decisions"
where search @@ websearch_to_tsquery('english', 'party autonomy')
    or search @@ websearch_to_tsquery('simple', 'party autonomy')

union all

-- Search in "Legislation" table
select 
    'Legislation' as source_table,       -- Indicate the source table
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'party autonomy')) +
    ts_rank(search, websearch_to_tsquery('simple', 'party autonomy')) as rank
from "Legislation"
where search @@ websearch_to_tsquery('english', 'party autonomy')
    or search @@ websearch_to_tsquery('simple', 'party autonomy')

-- Combine results and order by rank
order by rank desc;
