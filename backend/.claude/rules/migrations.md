---
paths: ["alembic_views/**/*.py", "alembic_suggestions/**/*.py"]
---

Never run or create migrations. Leave these to the developer.

SQL views are managed by Alembic migrations in `alembic_views/`.

View types:
- **Base views** (`vw_*`): flatten NocoDB tables into query-friendly columns
- **Relation views** (`vw_*_relations`): pre-compute entity relationships as JSONB arrays
- **Search function** (`search_all_v2`): full-text search across all base views
- **Detail function** (`get_entity_detail`): single-entity lookup returning base + relation data
