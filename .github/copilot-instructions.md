# CoLD Web Application - Copilot Instructions

**ALWAYS reference these instructions first and only fallback to additional search and context gathering if the information in the instructions is incomplete or found to be in error.**

The Choice of Law Dataverse (CoLD) is a Nuxt 3 frontend with FastAPI backend web application that provides access to a curated knowledge base on choice of law in international contracts. The frontend is built with Vue.js, TypeScript, and TailwindCSS, while the backend uses Python FastAPI with SQLAlchemy.

## Working Effectively

### Prerequisites
- Node.js v20+ (tested with v20.19.5)
- Python 3.12+ (tested with Python 3.12.3)
- npm 10+ (tested with v10.8.2)
- pip3 24+ (tested with pip 24.0)

### Initial Setup Commands
Run these commands in order to bootstrap the development environment:

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install
# Takes: ~55 seconds. Warnings about deprecated packages are normal.
# Warnings about font providers (fonts.google.com, etc.) are normal in restricted environments.

# Navigate to backend directory  
cd ../backend

# Install backend dependencies
pip3 install -r requirements.txt
# Takes: ~30 seconds. Uses user installation if normal site-packages not writable.
```

### Frontend Development

#### Build Commands
```bash
cd frontend

# Development server
npm run dev
# Takes: ~30 seconds to start, runs on http://localhost:3000
# IMPORTANT: Font provider warnings are NORMAL in sandboxed environments
# Server is ready when you see "Vite server built" and "Nuxt Nitro server built"

# Production build
npm run build  
# Takes: 3-4 minutes. NEVER CANCEL - set timeout to 300+ seconds minimum.
# Warnings about font providers are normal and do not affect functionality.
# Success indicated by "You can preview this build using `node .output/server/index.mjs`"

# Preview production build
npm run preview
# Starts preview server for production build testing

# Generate static files
npm run generate
# For static site generation
```

#### Linting and Formatting
```bash
cd frontend

# Format code with Prettier
npx prettier --write .
# Formats according to .prettierrc config (singleQuote: true, semi: false)

# Check formatting without fixing
npx prettier --check .

# ESLint (needs migration from v8 to v9 config format)
# Current .eslintrc.js needs to be migrated to eslint.config.js
# Run ESLint directly at your own risk - may fail without migration
```

### Backend Development

#### Running the Backend
```bash
cd backend

# Start development server  
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Runs on http://0.0.0.0:8000
# API docs available at http://localhost:8000/api/v1/docs
# NOTE: Requires database connection for full functionality
```

#### Testing
```bash
cd backend

# Run transformation tests (work without database)
PYTHONPATH=/home/runner/work/cold-web-app/cold-web-app/backend python3 tests/debug_frontend_fields.py
# Tests frontend field requirements and transformations

# Full test suite (requires database configuration)
python3 -m pytest tests/ -v
# Will fail without SQL_CONN_STRING environment variable
```

#### Linting and Formatting
```bash
cd backend

# Check code formatting with Black
python3 -m black --check .
# Shows files that would be reformatted

# Apply Black formatting
python3 -m black .
# Formats all Python files according to Black standards
```

### Build Timing and Timeout Guidelines

**CRITICAL: NEVER CANCEL BUILDS OR LONG-RUNNING COMMANDS**

| Command | Expected Time | Minimum Timeout | Notes |
|---------|---------------|-----------------|-------|
| `npm install` | 55 seconds | 180 seconds | Font provider warnings normal |
| `npm run build` | 3-4 minutes | 300 seconds | NEVER CANCEL - font warnings normal |
| `npm run dev` | 30 seconds | 120 seconds | Ready when Vite/Nitro servers built |
| `pip install -r requirements.txt` | 30 seconds | 120 seconds | User install warnings normal |
| Backend tests | 1-5 seconds | 60 seconds | Database-dependent tests will fail |

### Manual Validation Requirements

After making any code changes, ALWAYS perform these validation steps:

#### Frontend Validation
1. **Build Test**: Run `npm run build` and ensure it completes without errors
2. **Dev Server Test**: Run `npm run dev` and verify server starts successfully
3. **Basic Functionality**: 
   - Access http://localhost:3000 
   - Verify HTML content loads (should see DOCTYPE html with Nuxt UI styles)
   - Check browser console for JavaScript errors
4. **Format Check**: Run `npx prettier --check .` to ensure code formatting

#### Backend Validation  
1. **Transformation Test**: Run `PYTHONPATH=backend python3 backend/tests/debug_frontend_fields.py`
   - This tests data transformation logic without requiring database connection
   - Should show "Testing Frontend Field Requirements" and field validation results
2. **Format Check**: Run `python3 -m black --check backend/` to check code formatting
3. **Import Test**: Backend imports require database configuration and will fail without SQL_CONN_STRING

### Environment Variables and Configuration

#### Frontend (.env)
```bash
# Optional - for external font providers
NUXT_TURNSTILE_SITE_KEY=your-turnstile-site-key
NUXT_TURNSTILE_SECRET_KEY=your-turnstile-secret-key  
API_BASE_URL=https://your-api-endpoint
FASTAPI_API_TOKEN=your-api-token
NUXT_SITE_URL=https://your-site-url
NUXT_SITE_NAME="Your Site Name"
```

#### Backend (.env)
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

### Known Limitations and Workarounds

#### Font Provider Warnings
- **Issue**: Cannot connect to fonts.google.com, fonts.bunny.net, etc. in restricted environments
- **Impact**: Warning messages during build/dev, but functionality unaffected
- **Workaround**: Warnings are normal and safe to ignore

#### Docker Builds
- **Issue**: `docker build` fails in sandboxed environments due to certificate/network restrictions
- **Impact**: Cannot test Docker builds locally in restricted environments  
- **Workaround**: Docker builds work in proper environments with network access

#### Backend Database Requirements
- **Issue**: Many backend routes require database connection
- **Impact**: Backend server fails to start without proper database configuration
- **Workaround**: Use transformation tests that work without database connection

#### ESLint Configuration
- **Issue**: Current .eslintrc.js uses deprecated ESLint v8 format
- **Impact**: Direct ESLint execution may fail
- **Workaround**: Use Prettier for formatting until ESLint config is migrated

### Project Structure Quick Reference

```
frontend/
├── package.json          # Dependencies and scripts
├── nuxt.config.ts       # Nuxt configuration
├── .prettierrc          # Prettier formatting rules
├── .eslintrc.js         # ESLint config (needs v9 migration)
├── app.vue              # Root Vue component
├── pages/               # Route pages
├── components/          # Vue components  
├── composables/         # Vue composables
├── assets/              # CSS and static assets
└── public/              # Public static files

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

### CI/CD Integration

The project uses GitHub Actions for deployment:
- Frontend: `.github/workflows/deploy-frontend.yml`
- Backend: `.github/workflows/deploy-backend.yml`

Always run local validation before pushing:
```bash
# Frontend pre-commit checks
cd frontend && npm run build && npx prettier --check .

# Backend pre-commit checks  
cd backend && python3 -m black --check . && PYTHONPATH=backend python3 tests/debug_frontend_fields.py
```

### Debugging Common Issues

1. **"Module not found" errors in backend tests**: Set `PYTHONPATH=backend` before running tests
2. **Font provider connection errors**: Normal in restricted environments, safe to ignore
3. **ESLint configuration errors**: Use Prettier instead until config migration
4. **Build timeouts**: Increase timeout values - builds can take 3-4 minutes
5. **Database connection errors**: Expected without proper environment configuration

### Performance Expectations

- Frontend hot reload: ~1-2 seconds for most changes
- Frontend full rebuild: 3-4 minutes  
- Backend server startup: ~5-10 seconds (with database) 
- Test execution: 1-5 seconds for transformation tests
- Prettier formatting: 1-3 seconds for entire codebase