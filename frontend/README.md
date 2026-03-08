# Frontend - Nuxt 4 Application

Nuxt 4 frontend for the Choice of Law Dataverse (CoLD), built with Vue.js, TypeScript, TailwindCSS, and Nuxt UI 4.

> **For AI coding agents**: See [AGENTS.md](AGENTS.md) for agent-specific instructions.

## Prerequisites

- **Node.js v20+** (tested with v20.19.5)
- **pnpm 10+**

## Setup

```bash
pnpm install
```

## Development

```bash
pnpm run dev      # http://localhost:3000
```

## Production

```bash
pnpm run build    # Build for production
pnpm run preview  # Preview production build
```

## Before Committing

**Always run the validation checks:**

```bash
pnpm run check
```

This runs (in order): Prettier format, ESLint fix, vue-tsc type check, Vitest tests.

Individual commands:

```bash
pnpm run format        # Fix formatting
pnpm run lint:fix      # Fix lint issues
pnpm run typecheck     # Type check only
pnpm run test:run      # Run tests only
pnpm run build         # Verify build works
```

## API Type Generation

Types are generated from the backend's OpenAPI schema for end-to-end type safety:

```bash
pnpm run generate:api
```

This exports the backend's OpenAPI schema and generates `app/types/api-schema.d.ts`. Requires the backend Python environment. See [AGENTS.md](AGENTS.md) for details.

## Architecture

### Data Flow

1. Detail pages use `[coldId]` route params (e.g., `/court-decision/CH_2023_001`)
2. Data is fetched via typed composables (`useRecordDetails`, `useFullTable`) backed by TanStack Query
3. Types flow end-to-end: backend Pydantic models → OpenAPI schema → generated TypeScript types → Vue components

### Key Directories

| Directory             | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| `app/pages/`          | File-based routing (`[coldId].vue` for detail pages) |
| `app/components/`     | Vue components organized by feature                  |
| `app/composables/`    | Shared logic (`useX.ts` pattern)                     |
| `app/types/`          | TypeScript types including generated API schema      |
| `app/types/entities/` | Per-entity types with processor functions            |
| `app/config/`         | Labels, tooltips, navigation, card configs           |
| `app/utils/`          | Pure utility functions                               |

## Code Standards

- **TypeScript only**: `.ts` and `.vue` with `<script setup lang="ts">`, never `.js`
- **Composition API**: Vue Composition API with composables
- **No barrel files**: Import directly from specific modules
- **Conventional commits**: `type(scope): description`

See [AGENTS.md](AGENTS.md) for detailed coding conventions.

## Docker (Production Only)

Docker is only used for production deployment. Local development should use pnpm directly.

```bash
docker build -t cold-nuxt-frontend .
docker run -p 3000:3000 cold-nuxt-frontend
```
