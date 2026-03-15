---
paths: ["app/schemas/**/*.py"]
---

All request/response validation uses Pydantic v2 models defined here.
Use `Field(...)` for validation constraints.
`records.py` has shared `coerce_bools_to_str` validator — reuse it in new models.
