FastAPI backend (Python 3.12, SQLAlchemy, Pydantic v2). Uses `uv` for package management.

## Setup

```bash
cd backend
uv sync --all-extras --all-packages --group dev  # or: make setup
make dev  # http://localhost:8000
```

## API Auth

- Read-only data endpoints: publicly accessible (no auth required)
- Frontend requests: `X-API-Key` header
- User endpoints (suggestions): Auth0 JWT
- Admin endpoints: Auth0 JWT with roles

## Common Tasks

- **Add a route**: Create in `app/routes/` and register in `app/main.py`
- **Add a schema**: Create Pydantic model in `app/schemas/`
- **Add dependencies**: `uv add <package>` (not pip install)
- **Migrations**: Never run or create migrations. Leave these to the developer.

## SQL Views Architecture

Data is served through SQL views managed in `alembic_views/`:

- **Base views** (`vw_*`): flatten NocoDB tables into query-friendly columns
- **Relation views** (`vw_*_relations`): pre-compute entity relationships as JSONB arrays
- **Search function** (`search_all_v2`): full-text search across all base views
- **Detail function** (`get_entity_detail`): single-entity lookup returning base + relation data

Relation sort order belongs in `data_views.get_entity_detail` (jsonb_agg ORDER BY), not in Python services or frontend comparators.

## Common Issues

- **Import errors**: Run `uv sync` to rebuild environment
- **Command not found**: Use `uv run <command>` or `make <target>`
