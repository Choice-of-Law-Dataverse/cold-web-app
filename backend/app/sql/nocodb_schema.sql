SELECT
  table_schema || '.' || table_name AS table_full_name,
  column_name,
  ordinal_position,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'p1q5x3pj29vkrdr'
ORDER BY table_schema, table_name, ordinal_position;