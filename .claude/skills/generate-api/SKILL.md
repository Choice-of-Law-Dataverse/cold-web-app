---
name: generate-api
description: Regenerate OpenAPI TypeScript types from the backend schema after model or endpoint changes
disable-model-invocation: true
---

Regenerate the frontend's OpenAPI types from the backend:

1. Run `cd frontend && pnpm run generate:api`
2. Verify the generated types in `frontend/app/types/api-schema.d.ts` compile cleanly with `pnpm run typecheck`
3. Report what changed in the generated types
