---
paths: ["app/types/api-schema.d.ts", "app/types/openapi.json"]
---

These files are auto-generated. Do not edit manually.

Regenerate after any backend route/schema/Pydantic model change:

```bash
cd frontend && pnpm run generate:api
```

Requires backend Python environment to be set up locally.

Deploy gate: the frontend deploy workflow verifies committed types match the production API. If they diverge, either deploy backend first or regenerate types against current prod API.
