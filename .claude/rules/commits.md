Commits must follow: `type(optional scope): description`

Types: `feat`, `fix`, `perf`, `revert`, `refactor`, `docs`, `style`, `test`, `build`, `ci`, `chore`

Scopes are optional. Never use `frontend` or `backend` as a scope — Release Please assigns each
commit to a package by the file paths it touches, so a package-name scope that disagrees with the
diff is misleading. Use the domain instead (`case-analyzer`, `search`, `auth`, `views`, `entities`,
`ui`), or omit the scope for repo-wide changes.

Breaking changes take `!` before the colon (`feat(entities)!: ...`), which bumps the major version.

Never hand-edit a version or a `CHANGELOG.md`. Versions in `frontend/package.json`,
`backend/pyproject.toml`, and `.release-please-manifest.json` are written by the release pull
request.
