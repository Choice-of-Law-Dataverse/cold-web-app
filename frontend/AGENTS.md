Nuxt 4 frontend (Vue.js, TypeScript, TailwindCSS, Nuxt UI 4).

## Key Configuration

- **Auto-imports**: Only `vue` preset (configured in `nuxt.config.ts`). Custom composables, utils, and third-party libraries require explicit imports.
- **Color mode**: Light only (no dark mode)
- **Type checking**: Run `pnpm run check` (disabled in nuxt.config)

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
- **Backend schema changed**: Run `pnpm run generate:api`
