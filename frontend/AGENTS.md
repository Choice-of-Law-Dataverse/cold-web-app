Nuxt 4 frontend (Vue.js, TypeScript, TailwindCSS, Nuxt UI 4). Light mode only — no dark mode.

## Key Configuration

- **Auto-imports**: Vue/Nuxt built-ins (`ref`, `computed`, `useRoute`, etc.) are auto-imported. Custom composables, utils, and third-party libraries require explicit imports.
- **Color mode**: Light only (no dark mode)
- **Type checking**: Run `pnpm run check` (type checking is disabled in nuxt.config — run it manually)

## Setup

```bash
cd frontend && pnpm install
pnpm run dev      # http://localhost:3000
```

## Route Params

All detail pages use `[coldId]` as the route parameter. Access via `route.params.coldId`.

## Common Tasks

- **New detail page**: Add `pages/[entity]/[coldId].vue`, create entity type in `types/entities/`, register in `config/entityRegistry.ts`
- **New composable**: Add to `composables/` as `useFeatureName.ts`
- **New component**: Add to `components/` organized by feature — never create barrel files
- **Backend schema changed**: Run `pnpm run generate:api`

## Entity Type Pattern

Each entity file in `types/entities/` exports three things:

1. **Response type** — list/table row shape from `api-schema.d.ts`
2. **Detail response type** — full detail shape
3. **Processor function** — transforms raw API response into display-ready form

New entities must also be registered in `types/api.ts` type maps and `config/entityRegistry.ts`.

## Generated Types

`app/types/api-schema.d.ts` and `app/types/openapi.json` are auto-generated. Never edit manually. Regenerate with `pnpm run generate:api` after backend schema changes.

## Common Issues

- **Import errors after pull**: Run `pnpm install` then `pnpm run postinstall`
- **Type errors in api-schema.d.ts**: Regenerate with `pnpm run generate:api`
- **Build failures**: Check `pnpm run typecheck` output first
