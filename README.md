# CoLD Web App

Repository for the [Choice of Law Dataverse](https://cold.global) (CoLD) — an open-access knowledge base on choice of law in international contracts, developed at the University of Lucerne. Winner of the [Swiss National ORD Prize 2025](https://ord.swiss-academies.ch/news/swiss-national-ord-prize-2025-for-legal-and-environmental-sciences). Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> **For AI coding agents**: See [AGENTS.md](AGENTS.md) for agent-specific instructions.

## Quick Start

### Prerequisites

- **Node.js v20+** with pnpm 10+
- **Python 3.12** (managed by uv)
- **uv** (Python package manager): `brew install uv` (macOS) or see [uv docs](https://docs.astral.sh/uv/)

### Running Locally

```bash
# Frontend (in one terminal)
cd frontend
pnpm install
pnpm run dev
# Open http://localhost:3000/

# Backend (in another terminal)
cd backend
make setup
make dev
# API docs at http://localhost:8000/api/v1/docs
```

## Development Workflow

### Before Committing

Always run validation checks before committing:

```bash
# Frontend validation
cd frontend && pnpm run check

# Backend validation
cd backend && make check
```

### Code Standards

- **Conventional Commits**: `type(scope): description` — types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **No Barrel Files**: Avoid `index.ts`/`index.js`/`__init__.py` re-exports
- **TypeScript Only**: All frontend code must be `.ts` or `.vue` (never `.js`)

See [AGENTS.md](AGENTS.md) for detailed coding conventions.

## Project Structure

- **[frontend/](frontend/)**: Nuxt 4 application — see [frontend/README.md](frontend/README.md)
- **[backend/](backend/)**: FastAPI application — see [backend/README.md](backend/README.md)
- **[AGENTS.md](AGENTS.md)**: Instructions for AI coding agents

## API Documentation

The public API serves 17 datasets (court decisions, instruments, literature, arbitral awards, and more) across 63+ jurisdictions. Read-only data endpoints are publicly accessible — no API key required.

- **Production**: [api.cold.global/api/v1/docs](https://api.cold.global/api/v1/docs)
- **Local**: [localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Bulk exports**: [cold.global/data-sets](https://cold.global/data-sets) (CSV and XLSX)

## Further Resources

- **[Tech Wiki](https://choice-of-law-dataverse.github.io/)** — architecture documentation and technical decisions
- **[Glossary](https://cold.global/learn/glossary)** — private international law terms used across the platform
- **[Methodology](https://cold.global/learn/methodology)** — how the CoLD questionnaire is structured and data is collected

## Versioning and Deployment Policy

We continuously deploy the backend and frontend independently. Each component evolves at its own pace, with versioning applied as changes are introduced.

When creating an official release, we align the version numbers of the backend and frontend to the highest version between the two, ensuring consistency.

## Language Style Guide

For website and data input:

- Language: `en-US` — English as used in the United States
- Use the [Oxford comma](https://en.wikipedia.org/wiki/Serial_comma)
- Apply "Bluebook" title case style for titles, convert titles [here](https://titlecaseconverter.com/)
- When in doubt, look to [George](https://en.wikipedia.org/wiki/Politics_and_the_English_Language#Remedy_of_Six_Rules)

Legal terminology:

- non-State law
