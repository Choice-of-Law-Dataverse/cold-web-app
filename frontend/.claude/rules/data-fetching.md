---
paths: ["app/composables/**/*.ts"]
---

Data fetching uses TanStack Query (`@tanstack/vue-query`) via typed composables:

- `useRecordDetails(table, id, process?)` — single record by table name and ID
- `useFullTable(table, filters?)` — paginated table data with typed filters
- Entity-specific composables are convenience wrappers (e.g., `useCourtDecision(id)`)

Retries are disabled in dev mode for faster feedback.
