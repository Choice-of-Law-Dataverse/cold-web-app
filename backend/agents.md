# Backend - Agent Instructions

**Always reference these instructions first and only fallback to additional search and context gathering if the information in the instructions is incomplete or found to be in error.**

This is the backend subproject of the CoLD (Choice of Law Dataverse) web application, built with FastAPI, Python, SQLAlchemy, and Pydantic.

## Code Standards

### Python Requirements

- **Python 3.12**: Use modern Python features (managed by uv)
- **Type hints**: Always include type annotations
- **Pydantic models**: Use for data validation and serialization
- **Conventional commits**: Use semantic commit messages (feat:, fix:, docs:, refactor:, test:, chore:)

### File Organization

- **No barrel files**: Avoid `__init__.py` files that import everything
- **Direct imports**: Import specific functions/classes from modules
- **Clear module structure**: Organize by domain/feature, not by type

## Setup and Development

### Prerequisites

- **uv**: Modern Python package manager (install via `brew install uv` on macOS)
- **Python 3.12**: Managed automatically by uv

### Initial Setup

```bash
cd backend

# Install dependencies with uv
uv sync --all-extras --all-packages --group dev
# Creates virtual environment and installs all dependencies
# Takes: ~30 seconds. Handles Python version management automatically.
```

### Development Commands

```bash
# Start development server with uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Runs on http://0.0.0.0:8000
# API docs available at http://localhost:8000/api/v1/docs
# NOTE: Requires database connection for full functionality

# Alternative: Use Makefile commands
make dev        # Start development server
make serve      # Start production server
```

### Makefile Commands

The project now includes a comprehensive Makefile for common development tasks:

```bash
# Setup and dependencies
make setup      # Complete setup for new developers (installs uv + syncs deps)
make sync       # Sync dependencies with uv

# Code quality
make format     # Format code with ruff (applies fixes)
make format-check  # Check code formatting without changes
make lint       # Lint code with ruff
make type-check # Run type checking with pyright

# Testing
make test       # Run tests
make coverage   # Run tests with coverage report
make coverage-html  # Generate HTML coverage report

# Development
make dev        # Start development server
make serve      # Start production server

# Maintenance
make clean      # Clean up generated files
make check      # Run all quality checks (format-check + lint + type-check + test)
make ci         # Run all CI checks (check + coverage)
make all        # Run everything (sync + check + coverage)

# Docker
make build      # Build Docker image
make up         # Start Docker container
```

## Testing

### Test Commands

```bash
# Run tests with uv
uv run pytest
# Or with Makefile
make test

# Run tests with coverage
make coverage        # Coverage report in terminal
make coverage-html   # Generate HTML coverage report in htmlcov/

# Run transformation tests (work without database)
uv run python tests/debug_frontend_fields.py
# Tests frontend field requirements and transformations
```

### Test Timing

| Command              | Expected Time | Notes                                                      |
| -------------------- | ------------- | ---------------------------------------------------------- |
| `uv sync`            | 30 seconds    | Dependency sync with virtual environment                   |
| Backend tests        | 1-5 seconds   | Database-dependent tests will fail without SQL_CONN_STRING |
| Transformation tests | 1-5 seconds   | Work without database                                      |

## Code Quality

### Linting and Formatting

```bash
# Format code with ruff (recommended)
make format
# Or directly: uv run ruff format && uv run ruff check --fix

# Check formatting without making changes
make format-check
# Or directly: uv run ruff format --check

# Lint code
make lint
# Or directly: uv run ruff check

# Type checking
make type-check
# Or directly: uv run pyright .

# Run all quality checks
make check
# Equivalent to: make format-check lint type-check test
```

### Validation Requirements

After making any code changes, ALWAYS perform these steps:

1. **Quick validation**: `make check` - runs formatting, linting, type checking, and tests
2. **Transformation Test**: `uv run python tests/debug_frontend_fields.py` - tests data transformation without database
3. **Coverage Test**: `make coverage` - ensures test coverage meets requirements

The new tooling provides comprehensive code quality checks:

- **Ruff**: Fast Python linting and formatting (replaces Black + flake8)
- **Pyright**: Type checking for Python
- **Pre-commit hooks**: Automatic code quality checks on commit

## Architecture

### Key Technologies

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation

### Project Structure

```
backend/
├── pyproject.toml      # Project configuration and dependencies (uv/pip compatible)
├── uv.lock            # Lock file for reproducible builds
├── Makefile           # Development workflow automation
├── app/
│   ├── main.py         # FastAPI application entry point
│   ├── routes/         # API route handlers
│   ├── services/       # Business logic services
│   ├── mapping/        # Data transformation configs
│   └── config.py       # Environment configuration
├── tests/              # Test files
└── sql/                # Database schemas
```

### Environment Variables

```bash
# Required for full functionality
SQL_CONN_STRING="your-database-connection-string"
MONGODB_CONN_STRING="your-mongodb-connection"
OPENAI_API_KEY="your-openai-key"
JWT_SECRET="your-jwt-secret"

# Optional
NOCODB_BASE_URL="your-nocodb-url"
NOCODB_API_TOKEN="your-nocodb-token"
```

## API Documentation

### Endpoints

- **Root**: `/api/v1` - Health check
- **Search**: Full-text search and data retrieval
- **AI**: AI-powered query classification
- **Sitemap**: Frontend URL generation
- **Landing Page**: Support endpoints for frontend
- **Submarine**: Demo/easter egg route

### Authentication

All endpoints (except root) require JWT token in Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Common Issues

### Python Environment

- **Issue**: Module import errors or dependency conflicts
- **Solution**: Use `uv sync` to ensure clean virtual environment with correct dependencies
- **Check**: `uv run python --version` should show Python 3.12.x

### Development Workflow

- **Issue**: "Command not found" errors for development tools
- **Solution**: Use `uv run <command>` or `make <target>` to ensure tools run in correct environment
- **Alternative**: Activate virtual environment with `source .venv/bin/activate`

### Code Quality Failures

- **Issue**: Pre-commit hooks or CI failing on formatting/linting
- **Solution**: Run `make format` to auto-fix most issues, then `make check` to verify
- **Prevention**: Use `make check` before committing changes

### Performance Expectations

- Project setup (`make setup`): 60-90 seconds (includes uv installation + sync)
- Development server startup: 3-5 seconds (faster with uv)
- Test execution: 1-5 seconds for transformation tests
- Code quality checks: 5-10 seconds for full suite

## Data Transformation System

The backend includes a sophisticated data transformation system:

- **Configuration-driven**: JSON files define transformation rules
- **Multiple table support**: Handles various data types (instruments, court decisions, etc.)
- **Legacy compatibility**: Maintains backward compatibility
- **Testing**: Comprehensive test suite for transformation logic

See `app/mapping/transformations/README.md` for detailed documentation.
