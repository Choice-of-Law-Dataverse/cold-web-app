# Backend - Agent Instructions

**Always reference these instructions first and only fallback to additional search and context gathering if the information in the instructions is incomplete or found to be in error.**

This is the backend subproject of the CoLD (Choice of Law Dataverse) web application, built with FastAPI, Python, SQLAlchemy, and Pydantic.

## Code Standards

### Python Requirements
- **Python 3.12+**: Use modern Python features
- **Type hints**: Always include type annotations
- **Pydantic models**: Use for data validation and serialization
- **Conventional commits**: Use semantic commit messages (feat:, fix:, docs:, refactor:, test:, chore:)

### File Organization
- **No barrel files**: Avoid `__init__.py` files that import everything
- **Direct imports**: Import specific functions/classes from modules
- **Clear module structure**: Organize by domain/feature, not by type

## Setup and Development

### Initial Setup
```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt
# Takes: ~30 seconds. Uses user installation if normal site-packages not writable.
```

### Development Commands
```bash
# Start development server  
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Runs on http://0.0.0.0:8000
# API docs available at http://localhost:8000/api/v1/docs
# NOTE: Requires database connection for full functionality
```

## Testing

### Test Commands
```bash
# Run transformation tests (work without database)
PYTHONPATH=/home/runner/work/cold-web-app/cold-web-app/backend python3 tests/debug_frontend_fields.py
# Tests frontend field requirements and transformations

# Full test suite (requires database configuration)
python3 -m pytest tests/ -v
# Will fail without SQL_CONN_STRING environment variable
```

### Test Timing
| Command | Expected Time | Notes |
|---------|---------------|-------|
| `pip install -r requirements.txt` | 30 seconds | User install warnings normal |
| Backend tests | 1-5 seconds | Database-dependent tests will fail |
| Transformation tests | 1-5 seconds | Work without database |

## Code Quality

### Linting and Formatting
```bash
# Check code formatting with Black
python3 -m black --check .
# Shows files that would be reformatted

# Apply Black formatting
python3 -m black .
# Formats all Python files according to Black standards
```

### Validation Requirements
After making any code changes, ALWAYS perform these steps:

1. **Transformation Test**: `PYTHONPATH=backend python3 backend/tests/debug_frontend_fields.py`
   - Tests data transformation logic without requiring database connection
   - Should show "Testing Frontend Field Requirements" and field validation results
2. **Format Check**: `python3 -m black --check backend/` - check code formatting
3. **Import Test**: Backend imports require database configuration and will fail without SQL_CONN_STRING

## Architecture

### Key Technologies
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation

### Project Structure
```
backend/
├── requirements.txt     # Python dependencies
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

### Database Requirements
- **Issue**: Many backend routes require database connection
- **Impact**: Backend server fails to start without proper database configuration
- **Solution**: Use transformation tests that work without database connection

### Module Import Errors
- **Issue**: "Module not found" errors in backend tests
- **Solution**: Set `PYTHONPATH=backend` before running tests

### Performance Expectations
- Backend server startup: ~5-10 seconds (with database)
- Test execution: 1-5 seconds for transformation tests
- Black formatting: 1-3 seconds for entire codebase

## Data Transformation System

The backend includes a sophisticated data transformation system:

- **Configuration-driven**: JSON files define transformation rules
- **Multiple table support**: Handles various data types (instruments, court decisions, etc.)
- **Legacy compatibility**: Maintains backward compatibility
- **Testing**: Comprehensive test suite for transformation logic

See `app/mapping/transformations/README.md` for detailed documentation.