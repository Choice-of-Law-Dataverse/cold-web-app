Nuxt 4 frontend (Vue, TypeScript, TailwindCSS, Nuxt UI 4). Light mode only — never add dark-mode
styles.

## Gotchas

- Only Vue/Nuxt built-ins (`ref`, `computed`, `useRoute`, …) are auto-imported. Import custom
  composables, utils and third-party libraries explicitly.
- Type checking is disabled in `nuxt.config`, so the dev server and build do not catch type errors.
  Run `pnpm run typecheck`.
- `app/types/api-schema.d.ts` and `app/types/openapi.json` are generated. Never edit them; run
  `pnpm run generate:api` instead.
- No `console.log` in production code.

## Common Tasks

- **New detail page**: add `pages/[entity]/[coldId].vue` (detail routes read `route.params.coldId`),
  add the entity type in `types/entities/`, and register it in `types/api.ts` and
  `config/entityRegistry.ts`.
- **New composable**: `composables/useFeatureName.ts`.
- **New component**: under `components/`, grouped by feature.

## Common Issues

- **Import errors after a pull**: run `pnpm install`, which also runs `nuxt prepare`.
- **Type errors in `api-schema.d.ts`**: run `pnpm run generate:api`.
