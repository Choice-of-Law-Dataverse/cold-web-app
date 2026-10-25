The Choice of Law Dataverse (CoLD) is a monorepo: a Nuxt 4 frontend in `frontend/` and a FastAPI
backend in `backend/`. Each package has its own `AGENTS.md` with package-specific setup, tasks and
gotchas.

## Database Constraints

IMPORTANT: Only a production database exists — there is no dev or staging environment.

- Never run or create database migrations; leave them to the developer.
- Never perform destructive database operations.

## Scoped Rules

Conventions live in `.claude/rules/`, `frontend/.claude/rules/` and `backend/.claude/rules/`. Claude
Code loads them automatically; other agents must read them before editing or reviewing a file.
Apply a rule without `paths` frontmatter everywhere. Apply a rule with `paths` only when one of its
globs matches the file's path relative to the directory that contains that rule's `.claude` folder.

## Commands

The root `package.json` is a task runner, not a pnpm workspace: it delegates to `pnpm --dir frontend`
and `make -C backend`. Every root script has a per-package equivalent.

- **Setup**: `pnpm run setup` — also run `pnpm install` at the root in every clone and `git worktree`,
  or the commit hooks are silently absent.
- **Dev**: `pnpm run dev:web` (port 3000) and `pnpm run dev:api` (port 8000). Both read `PORT`.
- **API types**: run `pnpm run generate:api` after any backend route or schema change.

## Verification

Prove each change with a check you ran, and report the command and its result rather than asserting
success. Fix root causes; do not silence a failing check.

- **While working**: run the narrowest check that covers the change, such as one test file or the
  package's typecheck.
- **Before committing**: run typecheck and tests for each package you touched —
  `pnpm --dir frontend run typecheck && pnpm --dir frontend run test:run`, or
  `make -C backend type-check test`. Do not commit if they fail.
- **Before pushing**: run `pnpm run check:ci`, the read-only suite CI enforces.
- **UI changes**: run the dev servers and check the affected page in a browser.

Do not format or lint by hand before committing. The pre-commit hook runs Prettier, `eslint --fix`
and `ruff` over staged files only and re-stages their fixes. `pnpm run check` and `make check`
rewrite every file in the package, so use them only when you intend to reformat.

## Commits and Releases

Commits follow `type(scope): description` (see `.claude/rules/commits.md`). Release Please assigns a
commit to `frontend` or `backend` by the paths it touches, then tags and deploys each package from
its release pull request. There is no deploy-from-branch path.

Never hand-edit `frontend/package.json` or `backend/pyproject.toml` versions,
`.release-please-manifest.json`, or any `CHANGELOG.md`; the release pull request owns them.
