# CoLD FASTAPI
[API Documentation](https://cold-container-test.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/docs)

## Local testing
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Development Workflow

### Code Quality Checks

This project uses automated quality checks that run on every PR:

- **Ruff**: Linting and code style checking
  ```bash
  make lint
  ```

- **Pyright**: Type checking
  ```bash
  make type-check
  ```

- **Pytest**: Unit tests
  ```bash
  make test
  ```

- **Docker Build**: Ensures the application can be built
  ```bash
  make build
  ```

Run all checks at once:
```bash
make check
```

These checks are automatically run by the PR workflow when changes are made to the `backend/` directory.
