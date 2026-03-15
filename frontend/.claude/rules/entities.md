---
paths: ["app/types/entities/**/*.ts"]
---

Each entity file exports three things:

1. **Response type** (e.g., `CourtDecisionResponse`) — list/table row shape from `api-schema.d.ts`
2. **Detail response type** (e.g., `CourtDecisionDetailResponse`) — full detail shape
3. **Processor function** (e.g., `processCourtDecision`) — transforms raw API response into display-ready form

New entities must also be registered in:

- `types/api.ts` type maps (`TableResponseMap`, `TableDetailMap`, `TableProcessedMap`)
- `config/entityRegistry.ts`
