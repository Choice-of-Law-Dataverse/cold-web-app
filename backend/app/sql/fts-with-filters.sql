-- COMBINED SEARCH WITH FILTERS (Chronological, Case-Insensitive, and Optional Filters)

-- Define filter values for tables, jurisdictions, and themes
with params as (
    select 
        array['Answers', 'Court decisions', 'Legislation', 'Literature']::text[] as tables, -- Example: ['Answers', 'Legislation']
        array['Vietnam', 'Argentina']::text[] as jurisdictions, -- Example: [] for no jurisdiction filter
        array[]::text[] as themes -- Example: [] for no themes filter
)

-- Search in "Answers" table
select 
    'Answers' as source_table,
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'hague principles')) +
    ts_rank(search, websearch_to_tsquery('simple', 'hague principles')) as rank
from "Answers", params
where 
    (array_length(params.tables, 1) is null or 'Answers' = any(params.tables)) -- Filter by table (skip if empty)
    and (
        array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
        or "Name (from Jurisdiction)" = any(params.jurisdictions)
    )
    and (
        array_length(params.themes, 1) is null -- Skip theme filter if empty
        or exists (
            select 1
            from unnest(params.themes) as theme_filter
            where "Themes" ILIKE '%' || theme_filter || '%'
        ) -- Case-insensitive partial match for themes
    )
    and (
        search @@ websearch_to_tsquery('english', 'hague principles')
        or search @@ websearch_to_tsquery('simple', 'hague principles')
    )

union all

-- Search in "Court decisions" table
select 
    'Court decisions' as source_table,
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'hague principles')) +
    ts_rank(search, websearch_to_tsquery('simple', 'hague principles')) as rank
from "Court decisions", params
where 
    (array_length(params.tables, 1) is null or 'Court decisions' = any(params.tables)) -- Filter by table (skip if empty)
    and (
        array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
        or exists (
			select 1
			from unnest(params.jurisdictions) as jurisdiction_filter
			where "Jurisdiction Names" ILIKE '%' || jurisdiction_filter || '%'
		)
    )
    and (
        array_length(params.themes, 1) is null -- Skip theme filter if empty
        or exists (
            select 1
            from unnest(params.themes) as theme_filter
            where "Themes" ILIKE '%' || theme_filter || '%'
        ) -- Case-insensitive partial match for themes
    )
    and (
        search @@ websearch_to_tsquery('english', 'hague principles')
        or search @@ websearch_to_tsquery('simple', 'hague principles')
    )

union all

-- Search in "Legislation" table
select 
    'Legislation' as source_table,
    "ID" as id,
    ts_rank(search, websearch_to_tsquery('english', 'hague principles')) +
    ts_rank(search, websearch_to_tsquery('simple', 'hague principles')) as rank
from "Legislation", params
where 
    (array_length(params.tables, 1) is null or 'Legislation' = any(params.tables)) -- Filter by table (skip if empty)
    and (
        array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
        or "Jurisdiction name" = any(params.jurisdictions)
    )
    and (
        array_length(params.themes, 1) is null -- Skip theme filter if empty
        or exists (
            select 1
            from unnest(params.themes) as theme_filter
            where "Themes name" ILIKE '%' || theme_filter || '%'
        ) -- Case-insensitive partial match for themes
    )
    and (
        search @@ websearch_to_tsquery('english', 'hague principles')
        or search @@ websearch_to_tsquery('simple', 'hague principles')
    )

union all

-- Search in "Literature" table
select 
    'Literature' as source_table,
    "ID"::text as id,
    ts_rank(search, websearch_to_tsquery('english', 'hague principles')) +
    ts_rank(search, websearch_to_tsquery('simple', 'hague principles')) as rank
from "Literature", params
where 
    (array_length(params.tables, 1) is null or 'Literature' = any(params.tables)) -- Filter by table (skip if empty)
    and (
        array_length(params.jurisdictions, 1) is null -- Skip jurisdiction filter if empty
        or "Jurisdiction" = any(params.jurisdictions)
    )
	and (
        array_length(params.themes, 1) is null -- Skip theme filter if empty
        or exists (
            select 1
            from unnest(params.themes) as theme_filter
            where "Themes" ILIKE '%' || theme_filter || '%'
        ) -- Case-insensitive partial match for themes
    )
	and (
        search @@ websearch_to_tsquery('english', 'hague principles')
        or search @@ websearch_to_tsquery('simple', 'hague principles')
    )

-- Combine results and order by rank
order by rank desc
LIMIT 150;

