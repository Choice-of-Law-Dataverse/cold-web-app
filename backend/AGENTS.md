# AGENTS.md - Backend

FastAPI backend application for CoLD. This file provides essential context for AI agents. Human developers should refer to [README.md](README.md).

## Tech Stack

- **Framework**: FastAPI (async Python web framework)
- **Language**: Python 3.12 (with type hints, managed by uv)
- **Database**: SQLAlchemy (ORM) + psycopg2 (PostgreSQL driver)
- **Validation**: Pydantic v2 (data models and validation)
- **Package Manager**: uv (replaces pip/poetry/virtualenv)
- **Testing**: pytest + pytest-asyncio + pytest-mock
- **Formatting/Linting**: ruff
- **Type Checking**: pyright
- **Monitoring**: logfire

## Environment Setup

**Critical**: This project uses `uv` for package management, not pip or poetry.

```bash
# Install uv
brew install uv  # macOS
# Windows/Linux: https://docs.astral.sh/uv/

# Install dependencies
cd backend
uv sync --all-extras --all-packages --group dev

# Or use Makefile
make setup

# Start dev server
make dev  # http://localhost:8000
```

**All Python commands must use `uv run`:**

```bash
uv run uvicorn app.main:app --reload  # Start server
uv run pytest                         # Run tests
uv run python script.py               # Run script
```

## File Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment config (loads from .env)
│   ├── auth.py              # Auth0 JWT + API key validation
│   ├── routes/              # API endpoints
│   │   ├── search.py        # Search endpoints
│   │   ├── ai.py            # AI query classification
│   │   ├── suggestions.py   # User suggestions
│   │   └── ...              # sitemap, statistics, landing_page, submarine
│   ├── services/            # Business logic layer
│   │   ├── search.py
│   │   ├── ai.py
│   │   ├── database.py
│   │   ├── db_manager.py
│   │   ├── transformers.py
│   │   └── ...              # Domain-specific transformers
│   ├── schemas/             # Pydantic models
│   │   ├── requests.py      # Request models
│   │   ├── responses.py     # Response models
│   │   └── suggestions.py   # Suggestions models
│   ├── mapping/
│   │   ├── configs/         # Python mapping configs (Pydantic models)
│   │   │   ├── answers_mapping.py
│   │   │   ├── court_decisions_mapping.py
│   │   │   ├── arbitral_awards_mapping.py
│   │   │   └── ...          # 15+ mapping files
│   │   └── enums.py         # Mapping enums
│   └── sql/                 # SQL queries
├── tests/                   # Test files (see tests/README.md)
├── pyproject.toml           # Project config + dependencies
├── uv.lock                  # Lock file (like package-lock.json)
└── Makefile                 # Development commands
```

## Code Conventions

### Python Style

- **Type hints always**: Annotate functions, variables, class attributes
- **Modern syntax**: Use `list[str]` not `List[str]` (Python 3.12+)
- **Imports at top only**: No inline imports
- **Import order**: stdlib → third-party → local (blank lines between)

```python
# ✅ Good
from typing import Optional
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.search import SearchService

def get_user(user_id: int) -> dict[str, str]:
    return {"id": str(user_id), "name": "Example"}

# ❌ Bad
def get_user(user_id):  # No type hints!
    return {"id": user_id}
```

### Pydantic Models (Required)

- **All request/response validation**: Use Pydantic models
- **Location**: Define in `app/schemas/`
- **Type everything**: Include type hints for all fields

```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str
    age: int | None = None
```

### Code Organization

- **No barrel files**: No `__init__.py` re-exports
- **Direct imports**: Import from specific modules
- **Domain structure**: Organize by feature, not by type

### Standards Reference

See [root AGENTS.md](../AGENTS.md) for monorepo-wide standards (commits, barrel files).

## Before Committing (CRITICAL)

**ALWAYS run validation:**

```bash
make check
```

This runs:

1. **Format** (ruff format - auto-fixes)
2. **Type check** (pyright)
3. **Tests** (pytest)

**Expectations**:

- All checks must pass
- No type errors (pyright must pass)
- No failing tests
- Use `uv run` for all Python commands

**Note**: `make check` auto-formats code. To check without modifying, use individual commands.

## Common Tasks

- **Add a route**: Create in `app/routes/` and register in `app/main.py`
- **Add a service**: Create in `app/services/` with business logic
- **Add a schema**: Create Pydantic model in `app/schemas/`
- **Add a test**: Create in `tests/` matching the file structure
- **Add dependencies**: Use `uv add <package>` (not pip install)
- **Run a script**: Use `uv run python script.py` (not python script.py)

## Environment Variables

Key vars (see [README.md](README.md) for complete list):

- `SQL_CONN_STRING`, `OPENAI_API_KEY`
- `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `API_KEY`

## API & Auth

**Routes**: `/api/v1/{search,ai,suggestions,sitemap,landing_page,statistics,submarine}`

**Auth**: Most endpoints need `X-API-Key` header. User endpoints (suggestions) need Auth0 JWT. Admin endpoints need Auth0 JWT with roles.

See [README.md](README.md) for full API documentation.

## Common Issues

- **Import errors**: Run `uv sync` to rebuild environment
- **Command not found**: Use `uv run <command>` or `make <target>`
- **Quality checks fail**: Run `make format` then `make check`

## Notes

- **Setup time**: ~60-90 seconds
- **Data transformation**: Config-driven system in `app/mapping/configs/` (Python/Pydantic models) + transformer services in `app/services/`

See [README.md](README.md) for full documentation.
