FastAPI backend (Python 3.12, SQLAlchemy, Pydantic v2). Uses `uv` for package management.

## Setup

```bash
cd backend
uv sync --all-extras --all-packages --group dev  # or: make setup
make dev  # http://localhost:8000
```

## API Auth

- Most endpoints: `X-API-Key` header
- User endpoints (suggestions): Auth0 JWT
- Admin endpoints: Auth0 JWT with roles

## Common Tasks

- **Add a route**: Create in `app/routes/` and register in `app/main.py`
- **Add a schema**: Create Pydantic model in `app/schemas/`
- **Add dependencies**: `uv add <package>` (not pip install)
- **Migrations**: Never run or create migrations. Leave these to the developer.

## Common Issues

- **Import errors**: Run `uv sync` to rebuild environment
- **Command not found**: Use `uv run <command>` or `make <target>`
