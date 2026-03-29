---
name: create-migration
description: Create a new Alembic database migration after SQLAlchemy model changes
disable-model-invocation: true
---

Create a new Alembic migration:

1. Ask the user for a migration message if not provided as an argument
2. Run `cd backend && uv run alembic revision --autogenerate -m "<message>"`
3. Review the generated migration file for correctness — check that upgrade and downgrade are both populated
4. Report the migration file path and a summary of the operations

IMPORTANT: Never run `alembic upgrade`, `alembic downgrade`, or any command that touches the database. There is only a production database — migrations are applied through the deployment pipeline.
