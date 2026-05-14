The Choice of Law Dataverse (CoLD) is a monorepo with a Nuxt 4 frontend and FastAPI backend.

## Architecture

- `frontend/` — Nuxt 4 app (Vue, TypeScript, Nuxt UI 4)
- `backend/` — FastAPI service (Python 3.12, SQLAlchemy, Pydantic v2)
- `.claude/rules/` — shared agent rules (commits, validation, no barrel files)
- `frontend/.claude/rules/` — frontend-specific rules (Vue, TypeScript, data fetching, entities, generated types)
- `backend/.claude/rules/` — backend-specific rules (Python style, schemas, migrations)

## Setup

- **Frontend**: `cd frontend && pnpm install`
- **Backend**: `cd backend && uv sync --all-extras --all-packages --group dev` (or `make setup`)

## Dev

- **Frontend**: `cd frontend && pnpm run dev` (port 3000)
- **Backend**: `cd backend && make dev` (port 8000)

## Validation

- **Frontend**: `cd frontend && pnpm run check` (Prettier, ESLint, vue-tsc, Vitest)
- **Backend**: `cd backend && make check` (ruff, pyright, pytest)

Always run validation before committing. Do not commit if checks fail.

## Cross-Package Workflows

- **Regenerate API types after backend schema changes**: `cd frontend && pnpm run generate:api`

## Database Constraints

- Only a production database exists — there is no dev or staging environment.
- Never run or create database migrations. Leave these to the developer.
- Never perform destructive database operations.
