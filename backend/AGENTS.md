FastAPI backend (Python 3.12, SQLAlchemy, Pydantic v2), managed with `uv`. Run Python through
`uv run` or `make`; add dependencies with `uv add`, never `pip install`. `make dev` also accepts
`HOST`.

## API Auth

- Read-only data endpoints: public.
- Frontend requests: `X-API-Key` header.
- User endpoints (suggestions): Auth0 JWT.
- Admin endpoints: Auth0 JWT with roles.

## Common Tasks

- **Add a route**: create it in `app/routes/` and register it in `app/main.py`.
- **Add a schema**: create a Pydantic model in `app/schemas/`.

## SQL Views

Data is served through SQL views managed by Alembic in `alembic_views/`:

- **Base views** (`vw_*`): flatten NocoDB tables into query-friendly columns.
- **Relation views** (`vw_*_relations`): pre-compute entity relationships as JSONB arrays.
- **`search_all_v2`**: full-text search across all base views.
- **`get_entity_detail`**: single-entity lookup returning base and relation data.

Relation sort order belongs in `data_views.get_entity_detail` (`jsonb_agg ... ORDER BY`), not in
Python services or frontend comparators.

## Configuration

`app/config.py` loads `.env` through pydantic-settings' `env_file`. This fills the `Config` object
only; it does **not** set `os.environ`. A library that reads its own environment variables (as
Logfire does with `LOGFIRE_TOKEN`) must be passed the value from `config` explicitly.

## Common Issues

- **Import errors**: run `uv sync`.
- **Command not found**: use `uv run <command>` or a `make` target.
