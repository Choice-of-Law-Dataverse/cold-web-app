# Backend - FastAPI Application

FastAPI backend for the Choice of Law Dataverse (CoLD), built with Python, SQLAlchemy, and Pydantic.

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

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

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
# Using uv (runs in managed virtual environment)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use Makefile
make dev
```

All Python commands should use `uv run` to ensure the correct environment:

```bash
uv run pytest              # Run tests
uv run python script.py    # Run a script
uv run ruff check          # Run linting
```

API will be available at:

- **Server**: http://0.0.0.0:8000
- **API Docs**: http://localhost:8000/api/v1/docs

**Note**: Full functionality requires database connection (see Environment Variables below).

## Database Migrations

Alembic manages the suggestions schema. Apply migrations before running the app:

```bash
# Uses SUGGESTIONS_SQL_CONN_STRING from .env (or ALEMBIC_SQL_CONN_STRING / -x sql-url override)
uv run alembic upgrade head

# Or via Makefile
make migrate_suggestions
```

To point Alembic at a different DSN, export `ALEMBIC_SQL_CONN_STRING` or pass an override:

```bash
ALEMBIC_SQL_CONN_STRING="postgresql://..." uv run alembic upgrade head
uv run alembic upgrade head -x sql-url="postgresql://..."
```

Create new revisions after updating `app/services/suggestions_schema.py`:

```bash
uv run alembic revision -m "short description"
```

## Before Committing

**Always run the validation checks:**

```bash
make check
```

This runs formatting, linting, type checking, and tests.

## Code Style

- **Type hints**: Always annotate functions and variables (use `list[str]` not `List[str]`)
- **Pydantic models**: Use for all request/response validation in `app/schemas/`
- **Import organization**: Group stdlib → third-party → local (with blank lines)
- **No barrel files**: Avoid `__init__.py` re-exports
- **Conventional commits**: Follow semantic commit format

See [AGENTS.md](AGENTS.md) for detailed coding conventions.

## Available Commands

See [Makefile](Makefile) for complete documentation. Common commands:

```bash
make setup        # First-time setup
make dev          # Start development server
make check        # Run all quality checks
make test         # Run tests
```

## Environment Variables

Create a `.env` file with required variables:

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

# Optional - NocoDB integration
NOCODB_BASE_URL="your-nocodb-url"
NOCODB_API_TOKEN="your-nocodb-token"
```

## API Documentation

Live API documentation: [CoLD Backend Docs](https://api.cold.global/api/v1/docs)

## Docker (Production Only)

**Docker is only used for production deployment. Local and agentic development should use uv directly.**

For production deployment, see [Dockerfile](Dockerfile) and [Makefile](Makefile) for Docker commands.
