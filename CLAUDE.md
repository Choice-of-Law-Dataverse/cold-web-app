# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Choice of Law Dataverse (CoLD) web application at www.cold.global. Monorepo with Nuxt 3 frontend and FastAPI backend, deployed independently.

## Common Commands

### Frontend (Nuxt 3)
```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
npm run check        # REQUIRED before committing: format, lint, typecheck, test
npm run build
```

### Backend (FastAPI)
```bash
cd backend
uv sync --all-extras --all-packages --group dev  # or: make setup
make dev             # http://localhost:8000, API docs at /api/v1/docs
make check           # REQUIRED before committing: format, typecheck, test
```

All Python commands must use `uv run` (e.g., `uv run pytest`, `uv run python script.py`).

## Architecture

### Frontend (frontend/)
- **Framework**: Nuxt 3 (Vue.js SSR), TypeScript strict, TailwindCSS, Nuxt UI
- **Routing**: File-based in `pages/`
- **State**: Vue Composition API + composables in `composables/` (useX.ts pattern)
- **Components**: `components/ui/` (reusable), `components/layout/`, `components/[feature]/`
- **Auto-imports**: Components and composables are auto-imported (no manual imports needed)

### Backend (backend/)
- **Framework**: FastAPI with Python 3.12, `uv` package manager
- **Entry**: `app/main.py`
- **Routes**: `app/routes/` - register new routes in main.py
- **Services**: `app/services/` - business logic layer
- **Schemas**: `app/schemas/` - Pydantic request/response models
- **Data transformation**: Config-driven system in `app/mapping/configs/` (Pydantic models)
- **Auth**: Auth0 JWT + API key (`X-API-Key` header)
- **API paths**: `/api/v1/{search,ai,suggestions,sitemap,landing_page,statistics,submarine}`, `/moderation`

## Code Standards

### Conventional Commits (Required)
Format: `type(scope): description`
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
Examples: `feat(search): add jurisdiction filter`, `fix(api): resolve null pointer`

### No Barrel Files (Strict)
Never create `index.ts`/`index.js`/`__init__.py` that re-export. Always import directly from specific files.

### Frontend TypeScript
- All code must be `.ts` or `.vue` with `<script setup lang="ts">`
- No `.js` files, no `any`, use `import type` for type-only imports

### Backend Python
- Type hints always, modern syntax (`list[str]` not `List[str]`)
- Pydantic models for all request/response validation
- Use `uv run` for all Python commands, `uv add <package>` for dependencies
