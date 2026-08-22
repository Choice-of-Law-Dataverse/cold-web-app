Always run validation before committing:

- Both packages: `pnpm run check`
- Frontend: `cd frontend && pnpm run check`
- Backend: `cd backend && make check`

These rewrite files (Prettier, `eslint --fix`, `ruff format`).

For a read-only pass/fail that leaves the working tree untouched — what CI enforces — use
`pnpm run check:ci`, `pnpm run check:ci:web`, or `cd backend && make check-ci`.

Do not commit if these fail.
