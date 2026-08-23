# Contributing to CoLD

Thanks for contributing to the [Choice of Law Dataverse](https://cold.global). This document
covers how we branch, commit, and merge. For architecture and local setup, start with the
[README](README.md); for the conventions AI coding agents follow, see [AGENTS.md](AGENTS.md).

## Getting Started

```bash
pnpm install       # root dev tooling — also installs the git hooks
pnpm run setup     # installs frontend (pnpm) and backend (uv) dependencies

pnpm run dev:web   # in one terminal  — http://localhost:3000/
pnpm run dev:api   # in another       — http://localhost:8000/api/v1/docs
```

Prerequisites and per-package alternatives are documented in the
[README Quick Start](README.md#quick-start).

## Branching

Branch off `main` and open your pull request against `main`. What is deployed is recorded by the
`frontend-v*` and `backend-v*` tags, not by a branch; see [Releases](#releases).

Name branches `<author>/<topic>` (for example `marcosmesser/split-comparison-table`) or
`task/<ticket>/<topic>` when the work has a tracker ID. The branch name is never used as a
commit message, so it only has to be recognizable in a branch list.

## Commits

Every commit message must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(optional scope): description
```

### Types

Only the eleven types below are accepted.

| Type       | Use for                                                     | Changelog                    |
| ---------- | ----------------------------------------------------------- | ---------------------------- |
| `feat`     | A new capability                                            | **Features**                 |
| `fix`      | A bug fix                                                   | **Bug Fixes**                |
| `perf`     | A change that improves performance                          | **Performance Improvements** |
| `revert`   | Reverting a previous change                                 | **Reverts**                  |
| `refactor` | A code change that neither fixes a bug nor adds a feature   | hidden                       |
| `docs`     | Documentation only                                          | hidden                       |
| `style`    | Formatting only — whitespace, semicolons, no meaning change | hidden                       |
| `test`     | Adding or correcting tests                                  | hidden                       |
| `build`    | Build system or external dependencies                       | hidden                       |
| `ci`       | CI configuration, workflows, and scripts                    | hidden                       |
| `chore`    | Anything else that does not touch src or test files         | hidden                       |

Version bumps follow the spec: `!` or a `BREAKING CHANGE` footer bumps **major**, `feat` bumps
**minor**, `fix` bumps **patch**. See [Releases](#releases).

### Scopes

Scopes are optional and unrestricted by the linter. Keep them lowercase and use the domain the
change lives in (e.g. `case-analyzer`, `search`, `auth`, `views`, `entities`, `ui`). **Do not use
package names (`frontend`, `backend`) as scopes** — Release Please assigns commits to packages by
the **file paths** they touch, not by the scope you write, so a scope that disagrees with the diff
is misleading. Omit the scope when a change is genuinely repo-wide.

### Description

The description is lower-case, imperative, and has no trailing period:

```
feat(entities): collapse long relations lists and show item count
fix(auth): recover from callback errors and hydrate user past CDN cache
ci: pin the uv setup action
```

### Breaking changes

Put `!` before the colon and explain the migration in the pull request body:

```
feat(entities)!: drop the legacy relation payload shape
```

Because a PR title is a single line, `!` is the only way to flag a break — the `BREAKING CHANGE:`
footer has nowhere to live once the title is squashed.

Individual commit messages are upheld in review. Because we squash merge, the **PR title** is the
line that actually lands in history and the one Release Please reads, so that is the one that has
to be right; see [Pull Requests](#pull-requests).

## Commit Hooks

`pnpm install` at the repository root installs a `pre-commit` hook (and a `pre-merge-commit`
companion, since merge commits skip `pre-commit`) that runs [lint-staged] over **staged files
only**:

| Staged path                                        | What runs                               |
| -------------------------------------------------- | --------------------------------------- |
| `frontend/**/*.{js,mjs,cjs,ts,vue}`                | `prettier --write`, then `eslint --fix` |
| `frontend/**/*.{json,jsonc,css,md,yml,yaml}`       | `prettier --write`                      |
| `backend/**/*.py`                                  | `ruff format`, then `ruff check --fix`  |
| Root files plus `.github/`, `.claude/`, `.gemini/` | `prettier --write`                      |

Anything the tools fix is re-staged for you. Anything they cannot fix — a type error, a lint rule
with no autofix — aborts the commit with the error. Unstaged changes in a partially staged file
are stashed and restored untouched, so the hook never commits work you did not stage.

The hook deliberately does **not** run type-checking or tests: they are too slow for every
commit, and CI covers them. Run `pnpm run check` yourself before pushing.

Two things worth knowing:

- **The hook is per-checkout.** `pnpm install` generates `.husky/_/`, which is not committed. Each
  fresh clone — and each `git worktree` — needs its own root `pnpm install` before hooks fire.
  Without it the hook is simply absent; nothing warns you.
- **Both toolchains are required.** The hook shells out to `pnpm` and `uv` regardless of which
  package you touched, so a backend-only contributor still needs Node installed and vice versa.

[lint-staged]: https://github.com/lint-staged/lint-staged

## Before You Push

Run validation from the repository root:

```bash
pnpm run check       # both packages — rewrites files (prettier, eslint --fix, ruff format)

pnpm run check:web   # or: cd frontend && pnpm run check
pnpm run check:api   # or: cd backend && make check
```

`pnpm run check:ci` runs the same checks read-only — formatting and lint are verified instead of
applied, so your working tree is left untouched. This is what CI enforces. Do not push if it fails.

If you changed backend Pydantic schemas, regenerate the frontend API types:

```bash
pnpm run generate:api
```

## Previews

Every pull request that touches the frontend gets a Vercel preview deployment, and that preview
talks to the **production backend**. The data you see is live data: browsing is safe, but treat
anything that writes — submitting a case analysis, saving a draft — as a change to production.

## Pull Requests

We **squash merge** every pull request, and GitHub composes the squash commit from the
**PR title and description**. That has two consequences:

1. **The PR title must be a valid `type(optional scope): description` line.** It becomes the
   commit subject on `main`, with the PR number appended automatically. Your individual commits
   are collapsed, so the title — not the last commit — is what shows up in `git log`, and it is
   what Release Please reads to decide version bumps. A malformed title is a failed check:
   `.github/workflows/pr-title.yml` validates it on every open, edit, reopen, and push.
2. **The PR description becomes the commit body.** Write it for someone reading history six
   months from now. Fill in [the template](.github/pull_request_template.md), and delete the
   HTML comment hints and any section you left empty — whatever stays in the description is
   copied verbatim into the commit.

Beyond that:

- Keep one pull request to one logical change. Split unrelated work into separate PRs.
- Open it as a draft while it is in progress, and mark it ready when CI is green.
- CI (`PR Checks`) runs backend and frontend validation plus end-to-end tests, path-filtered to
  the packages you touched. All checks must pass before merge.
- **What to Check** is written for the reviewer, not as a report on yourself. Point them at the
  preview paths worth clicking, the edge cases you exercised by hand and the ones you did not,
  and the data worth spot-checking. Leave out anything CI already reports.
- Address review comments with additional commits rather than a force-push, so reviewers can
  follow what changed. Squashing is handled at merge time.

## Releases

Releases are orchestrated by [Release Please](https://github.com/googleapis/release-please).
Nobody edits a version or a changelog by hand.

1. Every push to `main` runs `.github/workflows/release-please.yml`, which maintains a single
   open **release pull request** titled `chore: release main`.
2. That PR accumulates the version bumps and `CHANGELOG.md` entries implied by the conventional
   commits landed since the last release, for `frontend` and `backend` independently. Release
   Please assigns each commit to a package by the **file paths** it touches, so a PR spanning both
   packages releases both.
3. Merging the release PR tags each released package — `frontend-v1.0.0`, `backend-v1.0.0` — and
   publishes a GitHub Release per package.
4. Each tag push triggers `.github/workflows/deploy.yml`, which deploys **only** the package the
   tag names. The version becomes the container image tag.

So a release is one merge, and deployment is its consequence. Nothing deploys from a branch.

### Deploying by hand

`deploy.yml` also accepts `workflow_dispatch`. Run it from a tag ref to redeploy exactly that
package and version; run it from a branch and it deploys **both** packages at that commit, tagging
the images with the commit SHA. Keep this for incident response — the tag path is the normal one.

### Versions

`frontend/package.json` and `backend/pyproject.toml` hold the current version of each package, and
`.release-please-manifest.json` is Release Please's own record of them. All three are written by
the release PR. Do not edit them in a feature branch.

## Code Standards

- **No barrel files** — never create `index.ts`, `index.js`, or `__init__.py` that only
  re-export. Import directly from the module that defines the thing.
- **TypeScript only** on the frontend — all code is `.ts` or `.vue`, never `.js`.
- **Follow the local conventions** in `.claude/rules/`, `frontend/.claude/rules/`, and
  `backend/.claude/rules/`. They cover Vue and TypeScript patterns, data fetching, entity
  handling, Python style, and Pydantic schemas, and they apply to human contributors just as
  much as to agents.
- **User-facing copy** follows the [Language Style Guide](README.md#language-style-guide):
  `en-US`, Oxford comma, Bluebook title case for titles.

## Database Changes

Only a production database exists — there is no dev or staging environment. Do not write or run
migrations, and do not run destructive operations against it. If your change needs a schema
change, describe it in the pull request and leave the migration to a maintainer.

## Reporting Issues

Open a [GitHub issue](https://github.com/Choice-of-Law-Dataverse/cold-web-app/issues) with what
you expected, what happened, and the steps to reproduce. For data corrections — a wrong citation,
a mislabeled jurisdiction — say which record on [cold.global](https://cold.global) is affected.

## License

Contributions are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
the same license as the rest of the repository.
