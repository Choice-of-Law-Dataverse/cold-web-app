The Choice of Law Dataverse (CoLD) is a monorepo with a Nuxt 4 frontend and FastAPI backend.

## Architecture

- `frontend/` — Nuxt 4 app (Vue, TypeScript, Nuxt UI 4)
- `backend/` — FastAPI service (Python 3.12, SQLAlchemy, Pydantic v2)
- `.claude/rules/` — shared agent rules (commits, validation, no barrel files)
- `frontend/.claude/rules/` — frontend-specific rules (Vue, TypeScript, data fetching, entities, generated types)
- `backend/.claude/rules/` — backend-specific rules (Python style, schemas, migrations)

## Root Scripts

The root `package.json` delegates to each package (`pnpm --dir frontend`, `make -C backend`).
It is a task runner only — not a pnpm workspace. pnpm does not manage the backend's Python
dependencies, and `frontend/pnpm-lock.yaml` stays in `frontend/`.

Every root script has a direct per-package equivalent; use whichever fits what you are doing.

## Setup

- **Both**: `pnpm run setup`
- **Frontend**: `cd frontend && pnpm install`
- **Backend**: `cd backend && uv sync --all-extras --all-packages --group dev` (or `make setup`)

## Dev

- **Frontend**: `pnpm run dev:web` (or `cd frontend && pnpm run dev`) — port 3000
- **Backend**: `pnpm run dev:api` (or `cd backend && make dev`) — port 8000

Both servers read `PORT` from the environment, so `PORT=4000 pnpm run dev:api` works.

## Validation

- **Both**: `pnpm run check` — or `check:web` / `check:api` for one side
- **Frontend**: `cd frontend && pnpm run check` (Prettier, ESLint, vue-tsc, Vitest)
- **Backend**: `cd backend && make check` (ruff, pyright, pytest)

These **rewrite files** — Prettier, `eslint --fix`, and `ruff format` all write in place.

For a read-only pass/fail answer that leaves the working tree untouched, use
`pnpm run check:ci` (or `check:ci:web` / `check:ci:api`, `cd backend && make check-ci`).
This is what CI enforces.

Always run validation before committing. Do not commit if checks fail.

## Cross-Package Workflows

- **Regenerate API types after backend schema changes**: `pnpm run generate:api` (or `cd frontend && pnpm run generate:api`)

## Database Constraints

- Only a production database exists — there is no dev or staging environment.
- Never run or create database migrations. Leave these to the developer.
- Never perform destructive database operations.
