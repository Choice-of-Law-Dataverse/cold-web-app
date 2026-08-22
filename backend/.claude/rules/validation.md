Always run before committing:

```bash
make check
```

This runs: ruff format (auto-fixes), pyright type check, pytest tests.

Use `make check-ci` for the read-only equivalent (`ruff format --check`, `ruff check`
without `--fix`). This is what CI runs, so prefer it when you only need a pass/fail answer.

All checks must pass. Use `uv run` for all Python commands.
