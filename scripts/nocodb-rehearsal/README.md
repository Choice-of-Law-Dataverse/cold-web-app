# NocoDB upgrade rehearsal

This harness rehearses the production NocoDB metadata migration on a local PostgreSQL copy.
PostgreSQL and NocoDB publish their ports only on the host loopback interface.

The pinned rehearsal path is:

- PostgreSQL: `16` (the production major version)
- Current NocoDB: `0.263.8`
- Target NocoDB: `2026.08.2`

NocoDB's documented Docker upgrade process is to start the new image with the same database and
configuration. This harness does that only after recording a baseline from the current image.

## Prerequisites

- Docker Desktop, `uv`, and `curl`
- A custom-format PostgreSQL dump supplied securely by an authorized administrator
- Enough local disk for the private production dump and restored database

Supply `NOCODB_API_TOKEN` through a secure channel if the REST smoke test is required. Keep the
token, dump, and reports out of shell history, logs, commits, and issue comments. Reports default
to `.context/nocodb-rehearsal/`, which is gitignored.

## Run from a supplied dump

This is the default workflow because it does not access production infrastructure:

```bash
export DUMP_FILE=/absolute/path/to/cold.dump
# Export NOCODB_API_TOKEN separately through approved secret tooling.
pnpm run rehearse:nocodb restore
pnpm run rehearse:nocodb run
```

## Create the dump locally

Only an authorized operator should use this alternative. PostgreSQL connection URIs require the
username, password, and database name to be percent-encoded. Build the URI from separately
supplied components so reserved characters in credentials are not interpreted as URI delimiters:

```bash
encode_uri_component() {
  URI_COMPONENT="$1" uv run --frozen --directory backend python -c \
    'import os; from urllib.parse import quote; print(quote(os.environ["URI_COMPONENT"], safe=""))'
}

PROD_USER_ENCODED=$(encode_uri_component "$PROD_USER")
PROD_PASSWORD_ENCODED=$(encode_uri_component "$PROD_PASSWORD")
PROD_DATABASE_ENCODED=$(encode_uri_component "$PROD_DATABASE")
export PROD_CONN="postgresql://${PROD_USER_ENCODED}:${PROD_PASSWORD_ENCODED}@${PROD_HOST}:5432/${PROD_DATABASE_ENCODED}?sslmode=require"
unset PROD_USER_ENCODED PROD_PASSWORD_ENCODED PROD_DATABASE_ENCODED PROD_PASSWORD
pnpm run rehearse:nocodb all
```

The harness converts SQLAlchemy schemes such as `postgresql+psycopg://` to libpq's
`postgresql://`, removes the application-only `options` query parameter, preserves other query
parameters, and adds `sslmode=require` when absent. Credentials must still be percent-encoded
before they are supplied.

Across the two workflows, the harness:

1. uses the supplied dump, or creates one with the PostgreSQL 16 client when explicitly authorized;
2. builds a local PostgreSQL 16 image with the dump's `pg_cron` extension and restores the dump
   into a fresh local volume;
3. starts NocoDB `0.263.8` and records the baseline;
4. starts NocoDB `2026.08.2` against the same restored database;
5. captures both containers' migration logs and version responses;
6. refreshes all materialized views before every structural snapshot;
7. verifies all 69 `data_views` objects, non-empty view results, base-table row counts,
   `COLUMN_MAPPINGS`, junction-table keys, and uppercase jurisdiction filters;
8. exercises `MainDBWriter` insert/link behavior and, when `NOCODB_API_TOKEN` is set, the NocoDB
   REST read/create/link/read path; and
9. fails if the target snapshot differs from the baseline.

The smoke records are deleted from the local copy in `finally` blocks. A failed cleanup affects
only the disposable local database.

To repeat a rehearsal with the same dump, remove the old local volume first:

```bash
pnpm run rehearse:nocodb clean
pnpm run rehearse:nocodb restore
pnpm run rehearse:nocodb run
```

If the baseline has already completed and only a target API check needs to be repeated, reuse the
latest baseline snapshot:

```bash
pnpm run rehearse:nocodb target
```

Override a version explicitly when rehearsing a newer release:

```bash
TARGET_NOCO_VERSION=2026.09.0 pnpm run rehearse:nocodb run
```

## Manual gates

The harness intentionally does not perform these actions:

- Ask a developer to run `cd backend && SQL_CONN_STRING=postgresql://... make migrate-views` and
  confirm the Alembic views head applies cleanly. Repository policy reserves migrations for the
  developer.
- Run `cd backend && make check` with the local connection configured.
- Have an editor inspect the local NocoDB UI at <http://127.0.0.1:8080>.
- Upgrade the production Container App. Do that only after the PostgreSQL resizing work has landed
  and settled, with a fresh dump and an agreed low-traffic window.

Remove the disposable containers, private network, and database volume when finished:

```bash
pnpm run rehearse:nocodb clean
```

The dump and reports remain in `.context` until deliberately removed.
