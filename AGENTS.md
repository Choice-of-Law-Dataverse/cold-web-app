# AGENTS.md

The Choice of Law Dataverse (CoLD) is a monorepo with a Nuxt 3 frontend and FastAPI backend.

## For AI Coding Agents

This file provides essential context for AI agents working on this codebase. Human developers should refer to [README.md](README.md) for detailed documentation.

## Project Structure

- **[frontend/](frontend/)**: Nuxt 3 application (Vue.js, TypeScript, TailwindCSS) - see [frontend/AGENTS.md](frontend/AGENTS.md)
- **[backend/](backend/)**: FastAPI application (Python, SQLAlchemy, Pydantic) - see [backend/AGENTS.md](backend/AGENTS.md)

## Environment Setup

### Prerequisites

- **Node.js v20+** with npm 10+ (frontend)
- **Python 3.12** (backend, managed by uv)
- **uv** (backend package manager): `brew install uv` or see https://docs.astral.sh/uv/

### First-Time Setup

```bash
# Frontend
cd frontend && npm install

# Backend
cd backend && brew install uv && uv sync --all-extras --all-packages --group dev
# Or: make setup
```

## Code Standards (Monorepo-wide)

### Conventional Commits (Required)

All commits must follow format: `type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:

- `feat(search): add jurisdiction filter`
- `fix(api): resolve null pointer in case analyzer`
- `docs(backend): update environment variables`

### No Barrel Files (Strict)

Never create `index.ts`/`index.js`/`__init__.py` that re-export:

```typescript
// ❌ NEVER do this
export * from "./module1";
export * from "./module2";
```

Always import directly from specific files:

```typescript
// ✅ Always do this
import { functionA } from "./module1";
import { functionB } from "./module2";
```

### TypeScript Only (Frontend)

- All frontend code must be `.ts` or `.vue` with `<script setup lang="ts">`
- Never use `.js` files
- Use strong typing, avoid `any`

## Validation (CRITICAL)

**ALWAYS run before committing:**

```bash
# Frontend validation
cd frontend && npm run check

# Backend validation
cd backend && make check
```

These commands run formatting, linting, type checking, and tests. **Do not commit if these fail.**

## Detailed Documentation

For detailed setup, development, and testing instructions, see:

- Root: [README.md](README.md)
- Frontend: [frontend/README.md](frontend/README.md) and [frontend/AGENTS.md](frontend/AGENTS.md)
- Backend: [backend/README.md](backend/README.md) and [backend/AGENTS.md](backend/AGENTS.md)
