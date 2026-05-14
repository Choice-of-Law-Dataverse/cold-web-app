# Backend — FastAPI Application

FastAPI backend for the [Choice of Law Dataverse](https://cold.global), built with Python 3.12, SQLAlchemy, and Pydantic v2. Serves 17 datasets across 63+ jurisdictions via a public read-only REST API.

> **For AI coding agents**: See [AGENTS.md](AGENTS.md) for agent-specific instructions.

## Package Manager: uv

**This project uses [uv](https://docs.astral.sh/uv/) for Python package and project management.**

uv is a fast Python package installer and resolver, written in Rust. It manages:

- Python version (automatically installs Python 3.12)
- Virtual environment
- Project dependencies
- Script execution

### Installation

```bash
# macOS/Linux
brew install uv

# Or see: https://docs.astral.sh/uv/
```

### Setup

```bash
cd backend

# Install dependencies (creates venv + installs packages)
uv sync --all-extras --all-packages --group dev

# Or use Makefile
make setup
```

## Development

Start the development server:

```bash
make dev
```

All Python commands should use `uv run` to ensure the correct environment:

```bash
uv run pytest              # Run tests
uv run python script.py    # Run a script
uv run ruff check          # Run linting
```

API will be available at:

- **Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

Full functionality requires a database connection (see Environment Variables below).

## Database Migrations

### Suggestions Schema

Alembic manages the suggestions schema:

```bash
make migrate_suggestions
```

To point Alembic at a different DSN, export `ALEMBIC_SQL_CONN_STRING` or pass an override:

```bash
ALEMBIC_SQL_CONN_STRING="postgresql://..." uv run alembic upgrade head
uv run alembic upgrade head -x sql-url="postgresql://..."
```

### SQL Views (alembic_views)

A separate Alembic environment in `alembic_views/` manages SQL views and functions used for search, full-table listings, and detail endpoints. These views flatten and join NocoDB tables into query-friendly structures.

```bash
make migrate-views
```

View types:

- **Base views** (`vw_*`): flatten NocoDB tables into query-friendly columns
- **Relation views** (`vw_*_relations`): pre-compute entity relationships as JSONB arrays
- **Search function** (`search_all_v2`): full-text search across all base views
- **Detail function** (`get_entity_detail`): single-entity lookup returning base + relation data

## Before Committing

**Always run the validation checks:**

```bash
make check
```

This runs formatting (ruff), type checking (pyright), and tests (pytest).

## Code Style

- **Type hints**: Always annotate functions and variables (use `list[str]` not `List[str]`)
- **Pydantic models**: Use for all request/response validation in `app/schemas/`
- **Import organization**: Group stdlib → third-party → local (with blank lines)
- **No barrel files**: Avoid `__init__.py` re-exports
- **Conventional commits**: `type(scope): description`

See [AGENTS.md](AGENTS.md) for detailed coding conventions.

## Available Commands

See [Makefile](Makefile) for complete documentation. Common commands:

```bash
make setup        # First-time setup
make dev          # Start development server
make check        # Run all quality checks
make test         # Run tests
make coverage     # Run tests with coverage (95% threshold)
```

## Environment Variables

Create a `.env` file with required variables (see `.env.blueprint` for the full list):

```bash
# Required for full functionality
SQL_CONN_STRING="your-database-connection-string"
OPENAI_API_KEY="your-openai-key"

# Authentication (Auth0)
AUTH0_DOMAIN="your-auth0-domain"
AUTH0_AUDIENCE="your-auth0-audience"

# API validation
API_KEY="your-frontend-api-key"

# Suggestions database (required for migrations)
SUGGESTIONS_SQL_CONN_STRING="postgresql://user:pass@host:5432/suggestions"
```

## API Documentation

- **Production**: [api.cold.global/api/v1/docs](https://api.cold.global/api/v1/docs)
- **Local**: [localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

## Docker (Production Only)

**Docker is only used for production deployment. Local development should use uv directly.**

For production deployment, see [Dockerfile](Dockerfile) and [Makefile](Makefile) for Docker commands.
