The Choice of Law Dataverse (CoLD) is a monorepo with a Nuxt 4 frontend and FastAPI backend.

## Architecture

- `frontend/` — Nuxt 4 app (Vue, TypeScript, Nuxt UI 4)
- `backend/` — FastAPI service (Python 3.12, SQLAlchemy, Pydantic v2)
- `.claude/rules/` — shared Claude rules (commits, validation, no barrel files)

## Setup

- **Frontend**: `cd frontend && pnpm install`
- **Backend**: `cd backend && uv sync --all-extras --all-packages --group dev`

## Dev

- **Frontend**: `cd frontend && pnpm run dev` (port 3000)
- **Backend**: `cd backend && make dev` (port 8000)

## Cross-Package Workflows

- **Regenerate API types after backend schema changes**: `cd frontend && pnpm run generate:api`
