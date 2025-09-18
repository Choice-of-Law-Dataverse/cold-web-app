WITH core_tables AS (
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema LIKE 'p%'       -- <-- Adjust if your schema prefix changes
      AND table_type = 'BASE TABLE'
      AND table_name NOT LIKE '\\_%'   -- Exclude internal tables starting with _
      AND table_name NOT LIKE 'pg\\_%' -- Exclude system tables
),
m2m_tables AS (
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_name LIKE '\_nc\_m2m\_%'
      AND table_schema LIKE 'p%'
      AND table_type = 'BASE TABLE'
),
m2m_columns AS (
    SELECT
        m2m.table_schema AS m2m_schema,
        m2m.table_name   AS m2m_table,
        c.column_name,
        c.ordinal_position
    FROM m2m_tables m2m
    JOIN information_schema.columns c
      ON m2m.table_schema = c.table_schema AND m2m.table_name = c.table_name
    WHERE c.column_name LIKE '%\_id'
),
edges AS (
    -- For each m2m table, find which core table each column refers to
    SELECT
        c1.table_schema   AS core_schema_1,
        c1.table_name     AS core_table_1,
        m2m.table_schema  AS m2m_schema,
        m2m.table_name    AS m2m_table,
        m2m1.column_name  AS m2m_column_1,
        m2m2.column_name  AS m2m_column_2,
        c2.table_schema   AS core_schema_2,
        c2.table_name     AS core_table_2
    FROM core_tables c1
    JOIN m2m_columns m2m1
      ON m2m1.column_name = c1.table_name || '_id'
    JOIN m2m_columns m2m2
      ON m2m2.m2m_schema = m2m1.m2m_schema
     AND m2m2.m2m_table  = m2m1.m2m_table
     AND m2m2.column_name <> m2m1.column_name
    JOIN core_tables c2
      ON m2m2.column_name = c2.table_name || '_id'
    JOIN m2m_tables m2m
      ON m2m.table_schema = m2m1.m2m_schema
     AND m2m.table_name = m2m1.m2m_table
)
SELECT
    core_schema_1 AS from_schema,
    core_table_1  AS from_table,
    m2m_schema,
    m2m_table,
    m2m_column_1,
    core_schema_2 AS to_schema,
    core_table_2  AS to_table,
    m2m_column_2
FROM edges
ORDER BY from_schema, from_table, to_table;