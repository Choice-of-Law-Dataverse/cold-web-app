Always run before committing:

```bash
make check
```

This runs: ruff format (auto-fixes), pyright type check, pytest tests.

All checks must pass. Use `uv run` for all Python commands.
