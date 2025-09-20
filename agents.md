# CoLD Web Application - Agent Instructions

**Always reference these instructions first and only fallback to additional search and context gathering if the information in the instructions is incomplete or found to be in error.**

The Choice of Law Dataverse (CoLD) is a monorepo containing a Nuxt 3 frontend and FastAPI backend web application that provides access to a curated knowledge base on choice of law in international contracts.

## Project Structure

This is a monorepo with two main subprojects:

- **frontend/**: Nuxt 3 application (Vue.js, TypeScript, TailwindCSS)
- **backend/**: FastAPI application (Python, SQLAlchemy, Pydantic)

Each subproject has its own `agents.md` file with specific instructions.

## Global Guidelines

### Code Standards
- **No barrel files**: Avoid index.js/index.ts files that re-export everything
- **Conventional commits**: Use semantic commit messages (feat:, fix:, docs:, etc.)
- **TypeScript preference**: Use TypeScript for all frontend code; avoid plain JavaScript

### Development Workflow
1. Make changes in the appropriate subproject directory
2. Follow the specific instructions in each subproject's `agents.md`
3. Test changes in both development and production modes
4. Use conventional commit messages for all commits

### Prerequisites
- Node.js v20+ (tested with v20.19.5)
- Python 3.12+ (tested with Python 3.12.3)
- npm 10+ (tested with v10.8.2)
- pip3 24+ (tested with pip 24.0)

### Quick Start
```bash
# Frontend setup
cd frontend && npm install && npm run dev

# Backend setup (in new terminal)
cd backend && pip3 install -r requirements.txt
PYTHONPATH=backend python3 -m uvicorn app.main:app --reload
```

### CI/CD Integration
- Frontend deployment: `.github/workflows/deploy-frontend.yml`
- Backend deployment: `.github/workflows/deploy-backend.yml`

### Known Limitations
- Font provider warnings are normal in restricted environments
- Docker builds fail in sandboxed environments due to network restrictions
- Full backend functionality requires database configuration

## Validation Before Committing
```bash
# Frontend validation
cd frontend && npm run build && npx prettier --check .

# Backend validation  
cd backend && python3 -m black --check . && PYTHONPATH=backend python3 tests/debug_frontend_fields.py
```

See subproject-specific instructions in `frontend/agents.md` and `backend/agents.md` for detailed guidance.