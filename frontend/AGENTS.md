# AGENTS.md - Frontend

Nuxt 4 frontend application for CoLD. This file provides essential context for AI agents. Human developers should refer to [README.md](README.md).

## Tech Stack

- **Framework**: Nuxt 4 (Vue.js SSR meta-framework, SSR enabled)
- **Language**: TypeScript (strict mode, never JavaScript)
- **Styling**: TailwindCSS + SCSS
- **Components**: Nuxt UI 4
- **State**: Vue Composition API + composables pattern
- **Testing**: Vitest
- **Formatting**: Prettier
- **Linting**: ESLint
- **Auth**: Auth0 (@auth0/auth0-nuxt)
- **Maps**: Leaflet (@nuxtjs/leaflet)
- **Content**: Nuxt Content (@nuxt/content)

### Key Configuration Notes

- **Auto-imports**: Restricted to `vue` preset only (configured in nuxt.config.ts)
  - Vue/Nuxt built-ins (ref, computed, useRoute, etc.) are auto-imported
  - Custom components, composables, utils, and third-party libraries require explicit imports
- **Color mode**: Light mode only (no dark mode)
- **Type checking**: Disabled in nuxt.config (typeCheck: false) - run `pnpm run check` separately
- **Runtime config**: Uses environment variables for API, Auth0, R2 storage, and Logfire

## Environment Setup

```bash
cd frontend
pnpm install      # ~55 seconds (font warnings normal)
pnpm run dev      # http://localhost:3000
```

**Note**: Docker NOT needed for development (production only).

## File Structure

```
frontend/app/
├── pages/              # File-based routing ([coldId].vue for detail pages)
├── components/
│   ├── ui/             # Reusable UI components
│   ├── layout/         # Layout components (header, footer, etc.)
│   └── [feature]/      # Feature-specific components
├── composables/        # Shared logic (useX.ts pattern)
├── config/             # Labels, tooltips, navigation, card configs
├── types/
│   ├── entities/       # Per-entity types with processor functions
│   ├── api.ts          # Type maps (TableName, TableResponseMap, etc.)
│   ├── api-schema.d.ts # Generated from backend OpenAPI (do not edit)
│   └── openapi.json    # Exported OpenAPI schema (do not edit)
├── assets/             # Static assets, SCSS, data files
├── public/             # Public static files
└── utils/              # Pure utility functions
```

## Code Conventions

### TypeScript (Strict)

- **Always TypeScript**: Use `.ts` and `.vue` files, never `.js`
- **Strong typing**: Define interfaces/types, avoid `any`
- **Type imports**: Use `import type` for type-only imports

```typescript
// ✅ Good
import type { User } from '@/types';
interface Props {
  userId: string;
  isActive: boolean;
}

// ❌ Bad
import { User } from '@/types';  // Not type-only
const props: any = ...;  // No any!
```

### Vue.js (Composition API)

- **Always `<script setup lang="ts">`**: Never use Options API for new/touched code
- **Composables**: Extract shared logic to `composables/useFeatureName.ts`
- **Component naming**: PascalCase (e.g., `UserProfile.vue`)
- **Auto-imports**: Only Vue/Nuxt built-ins (ref, computed, useRoute, etc.) are auto-imported. Custom components, composables, utils, and third-party libraries require explicit imports.

```vue
<!-- ✅ Good -->
<script setup lang="ts">
import type { User } from "@/types";

const props = defineProps<{
  user: User;
}>();

const { data, isLoading } = useUserData(props.user.id);
</script>
```

### Imports (No Barrel Files)

- **No `index.ts` re-exports**: Import from specific files
- **Direct imports**: Always import from the actual file

```typescript
// ✅ Good
import { formatDate } from "@/utils/date";
import { UserCard } from "@/components/user/UserCard.vue";

// ❌ Bad
import { formatDate } from "@/utils"; // Barrel file
```

### Standards Reference

See [root AGENTS.md](../AGENTS.md) for monorepo-wide standards (commits, barrel files, etc.).

## Architecture

### End-to-End Type Safety

Types flow from backend to frontend without manual duplication:

1. Backend Pydantic models define the API schema
2. `pnpm run generate:api` exports the OpenAPI schema and generates `types/api-schema.d.ts`
3. `openapi-fetch` creates a typed API client (`composables/useApiClient.ts`)
4. Entity types in `types/entities/` define per-entity response types and processor functions
5. Type maps in `types/api.ts` (`TableResponseMap`, `TableDetailMap`, `TableProcessedMap`) power generic composables

### Data Fetching

Data fetching uses TanStack Query (`@tanstack/vue-query`) via typed composables:

- **`useRecordDetails(table, id, process?)`** — fetches a single record by table name and ID, with optional processor
- **`useFullTable(table, filters?)`** — fetches paginated table data with typed filters
- **Entity-specific composables** — convenience wrappers like `useCourtDecision(id)`, `useLiterature(id)`, etc.

Retries are disabled in dev mode for faster feedback.

### Entity Types (`types/entities/`)

Each entity file exports three things:

- **Response type** (e.g., `CourtDecisionResponse`) — list/table row shape from `api-schema.d.ts`
- **Detail response type** (e.g., `CourtDecisionDetailResponse`) — full detail shape
- **Processor function** (e.g., `processCourtDecision`) — transforms raw API response into display-ready form

### Config Directory (`config/`)

| File                | Purpose                                                                                         |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| `entityRegistry.ts` | Central entity config: field order, label overrides, content components, processing functions   |
| `tooltips.ts`       | Tooltip content per entity field, validated with `satisfies Partial<Record<FieldType, string>>` |
| `navigation.ts`     | App navigation structure                                                                        |
| `cardConfigs.js`    | Card layout configurations                                                                      |
| `assets.ts`         | Asset path helpers                                                                              |
| `auth.ts`           | Auth0 configuration                                                                             |

### Route Params

All detail pages use `[coldId]` as the route parameter (e.g., `/court-decision/CH_2023_001`). Access via `route.params.coldId`.

## Before Committing (CRITICAL)

**ALWAYS run validation:**

```bash
pnpm run check
```

This runs:

1. **Format check** (Prettier)
2. **Lint** (ESLint)
3. **Type check** (vue-tsc)
4. **Test** (Vitest)

**Expectations**:

- All checks must pass
- No TypeScript errors
- No console.log statements in production code
- Build must succeed: `pnpm run build`

## Component Map

Quick reference for finding components by feature area:

| Feature                 | Components                                      | Page                                       |
| ----------------------- | ----------------------------------------------- | ------------------------------------------ |
| Jurisdiction report     | `jurisdiction/JurisdictionComparisonTable.vue`  | `pages/jurisdiction/[coldId].vue`          |
| Jurisdiction picker     | `jurisdiction/JurisdictionSelectMenu.vue`       | multiple pages                             |
| Answer→jurisdiction map | `jurisdiction/QuestionAnswerMap.vue`            | `pages/question/[coldId].vue`              |
| Jurisdiction banner     | `jurisdiction/JurisdictionReportBanner.vue`     | question, instrument, court decision pages |
| Flag with coverage      | `jurisdiction/JurisdictionFlagWithCoverage.vue` | used by JurisdictionReportBanner           |
| Flag primitive          | `ui/JurisdictionFlag.vue`                       | 22+ usages across codebase                 |
| Case analyzer           | `case-analyzer/`                                | `pages/case-analyzer.vue`                  |
| Search                  | `search/`                                       | `pages/search.vue`                         |
| Landing page            | `landing-page/`                                 | `pages/index.vue`                          |
| Legal provisions        | `legal/`                                        | instrument and court decision pages        |
| Literature              | `literature/`                                   | multiple detail pages                      |

## API Type Generation

The frontend uses `openapi-fetch` with generated TypeScript types from the backend's OpenAPI schema.

**Generated files** (committed, marked `linguist-generated` in `.gitattributes`):

- `app/types/openapi.json` — OpenAPI schema exported from backend
- `app/types/api-schema.d.ts` — TypeScript types generated by `openapi-typescript`

**When to regenerate**: After any change to backend routes, request/response schemas, or Pydantic models.

```bash
cd frontend
pnpm run generate:api
```

This requires the backend Python environment to be set up locally. The script imports the FastAPI app, extracts the OpenAPI schema, filters to `/api/v1` paths, and generates TypeScript types.

**Deploy gate**: The frontend deploy workflow verifies that committed types match the production API. If they diverge, the deploy is blocked. To fix: either deploy backend first or regenerate types against the current prod API.

## Common Tasks

- **New detail page**: Add `pages/[entity]/[coldId].vue`, create entity type in `types/entities/`, register in `config/entityRegistry.ts`
- **New component**: Add to `components/[feature]/` (PascalCase)
- **New composable**: Add to `composables/` as `useFeatureName.ts`
- **New entity type**: Add to `types/entities/`, export response/detail types and processor function, register in `types/api.ts` type maps
- **Add field labels/tooltips**: Update `config/entityRegistry.ts` (labelOverrides) and optionally `config/tooltips.ts`
- **Backend schema changed**: Run `pnpm run generate:api` to regenerate types

See [README.md](README.md) for full documentation.
