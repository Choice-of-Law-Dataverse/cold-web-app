# AGENTS.md - Frontend

Nuxt 3 frontend application for CoLD. This file provides essential context for AI agents. Human developers should refer to [README.md](README.md).

## Tech Stack

- **Framework**: Nuxt 3 (Vue.js SSR meta-framework, SSR enabled)
- **Language**: TypeScript (strict mode, never JavaScript)
- **Styling**: TailwindCSS + SCSS
- **Components**: Nuxt UI library
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
- **Type checking**: Disabled in nuxt.config (typeCheck: false) - run `npm run check` separately
- **Runtime config**: Uses environment variables for API, Auth0, R2 storage, and Logfire

## Environment Setup

```bash
cd frontend
npm install      # ~55 seconds (font warnings normal)
npm run dev      # http://localhost:3000
```

**Note**: Docker NOT needed for development (production only).

## File Structure

```
frontend/
├── pages/           # File-based routing (add files here for new routes)
├── components/
│   ├── ui/          # Reusable UI components
│   ├── layout/      # Layout components (header, footer, etc.)
│   └── [feature]/   # Feature-specific components
├── composables/     # Shared logic (useX.ts pattern)
├── types/           # TypeScript type definitions
├── assets/          # Static assets, SCSS, data files
├── public/          # Public static files
└── utils/           # Utility functions
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

## Before Committing (CRITICAL)

**ALWAYS run validation:**

```bash
npm run check
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
- Build must succeed: `npm run build`

## Component Map

Quick reference for finding components by feature area:

| Feature                 | Components                                      | Page                                       |
| ----------------------- | ----------------------------------------------- | ------------------------------------------ |
| Jurisdiction report     | `jurisdiction/JurisdictionComparisonTable.vue`  | `pages/jurisdiction/[id].vue`              |
| Jurisdiction picker     | `jurisdiction/JurisdictionSelectMenu.vue`       | multiple pages                             |
| Answer→jurisdiction map | `jurisdiction/QuestionAnswerMap.vue`            | `pages/question/[id].vue`                  |
| Jurisdiction banner     | `jurisdiction/JurisdictionReportBanner.vue`     | question, instrument, court decision pages |
| Flag with coverage      | `jurisdiction/JurisdictionFlagWithCoverage.vue` | used by JurisdictionReportBanner           |
| Flag primitive          | `ui/JurisdictionFlag.vue`                       | 22+ usages across codebase                 |
| Case analyzer           | `case-analyzer/`                                | `pages/case-analyzer.vue`                  |
| Search                  | `search/`                                       | `pages/search.vue`                         |
| Landing page            | `landing-page/`                                 | `pages/index.vue`                          |
| Legal provisions        | `legal/`                                        | instrument and court decision pages        |
| Literature              | `literature/`                                   | multiple detail pages                      |

## Common Tasks

- **Page**: Add to `pages/` (file-based routing)
- **Component**: Add to `components/[feature]/` (PascalCase)
- **Composable**: Add to `composables/` as `useFeatureName.ts`
- **Types**: Define in `types/`

See [README.md](README.md) for full documentation.
