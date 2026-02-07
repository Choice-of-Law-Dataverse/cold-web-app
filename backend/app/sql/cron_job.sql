CREATE EXTENSION IF NOT EXISTS pg_cron;

SELECT cron.schedule(
  'refresh_nocodb_views',
  '*/15 * * * *',
  $$SELECT data_views.refresh_all_materialized_views();$$
);
