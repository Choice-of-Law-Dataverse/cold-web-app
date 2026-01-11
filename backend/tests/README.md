# Backend Tests

## Test Architecture

All tests are designed to run **without external dependencies** (no real SQL databases or internet access).

### Test Types

1. **Unit Tests** - Test individual functions/classes with mocked dependencies

   - Run in ~0.5 seconds
   - No external connections
   - Use fixtures and mocks

2. **Integration Tests** (Skipped in CI)
   - Require real database connections
   - Marked with `pytest.mark.skip`
   - Must be run manually with test databases
   - Example: `test_search_for_entry.py`

### How Tests Avoid External Dependencies

#### Database Connections

- Services use **dependency injection** (FastAPI's `Depends()`)
- Tests override dependencies with mock services
- `Database` class uses **lazy metadata loading** (no connection at instantiation)
- Integration tests use `sqlite:///:memory:` (in-memory, no external DB)

#### HTTP/API Calls

- Tests call **services directly**, not through HTTP routes
- No `TestClient` usage (avoids app lifespan/startup)
- Mock external API responses

### Running Tests

```bash
# Run all tests (skips integration tests)
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run only unit tests (explicitly)
uv run pytest -m "not integration"

# Run integration tests (requires test database)
uv run pytest tests/test_search_for_entry.py --run-integration
```

### CI/CD

Tests run in CI with `.blueprint.env` containing dummy connection strings:

- `SQL_CONN_STRING=postgresql://user:pass@localhost:5432/testdb`

These connections are never attempted because:

1. Services use dependency injection
2. Tests use mocks instead of real services
3. Database metadata loading is lazy
4. Integration tests are skipped

### Test Speed Expectations

| Environment             | Time  | Notes                              |
| ----------------------- | ----- | ---------------------------------- |
| CI (no real DB)         | ~1-2s | All mocked, 6 skipped              |
| Local (with real DB)    | ~0.5s | Real connections succeed instantly |
| Local (without real DB) | ~1-2s | Same as CI                         |

### Skipped Tests

Currently 6 tests are skipped:

- 4 tests that call internal methods with raw dicts (by design)
- 2 integration tests that require real database (test_search_for_entry.py)
