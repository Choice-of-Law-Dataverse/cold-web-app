import logging
from contextlib import asynccontextmanager

import logfire
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.routes import (
    ai,
    case_analyzer,
    entities,
    feedback,
    landing_page,
    search,
    sitemap,
    statistics,
    submarine,
    suggestions as suggestions_router,
)
from app.services.db_manager import db_manager, suggestions_db_manager
from app.services.http_session_manager import http_session_manager

# Configure logging to send to Logfire
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()), handlers=[logfire.LogfireLoggingHandler()])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    logger = logging.getLogger(__name__)

    with logfire.span("application_startup"):
        logger.info("Initializing connection pools...")

        if config.SQL_CONN_STRING:
            db_manager.initialize(
                connection_string=config.SQL_CONN_STRING,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                pool_pre_ping=True,
            )
            logger.info("Main database connection pool initialized")
        else:
            logger.warning("SQL_CONN_STRING not configured, database operations will fail")

        suggestions_conn = config.SUGGESTIONS_SQL_CONN_STRING or config.SQL_CONN_STRING
        if suggestions_conn:
            suggestions_db_manager.initialize(
                connection_string=suggestions_conn,
                pool_size=3,
                max_overflow=5,
                pool_recycle=3600,
                pool_pre_ping=True,
            )
            logger.info("Suggestions database connection pool initialized")

        http_session_manager.initialize(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3,
        )
        logger.info("HTTP session manager initialized")

        logger.info("All connection pools initialized successfully")

    yield

    with logfire.span("application_shutdown"):
        logger.info("Shutting down connection pools...")

        db_manager.dispose()
        suggestions_db_manager.dispose()

        http_session_manager.close()

        logger.info("Connection pools shut down successfully")


app = FastAPI(
    title="CoLD API — Choice of Law Dataverse",
    version="1.0.0",
    description=(
        "# Choice of Law Dataverse (CoLD) API\n\n"
        "Open-access REST API for the **[Choice of Law Dataverse](https://cold.global)**, "
        "a curated knowledge base on choice of law in international contracts. "
        "CoLD is an SNF-funded project at the University of Lucerne, licensed under "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
        "Winner of the Swiss National ORD Prize 2025.\n\n"
        "## Available datasets\n\n"
        "| Table name | Description |\n"
        "|---|---|\n"
        "| **Answers** | Country-level responses to the CoLD standardised questionnaire on choice-of-law rules |\n"
        "| **HCCH Answers** | Answers mapped to the HCCH Principles on Choice of Law |\n"
        "| **Questions** | The standardised questionnaire items that Answers respond to |\n"
        "| **Court Decisions** | Case law with metadata, themes, PIL provisions, and jurisdiction links |\n"
        "| **Domestic Instruments** | National statutes, codes, and PIL regulations |\n"
        "| **Domestic Legal Provisions** | Individual articles/provisions within domestic instruments |\n"
        "| **Regional Instruments** | Supranational instruments (e.g. EU Rome I Regulation) |\n"
        "| **Regional Legal Provisions** | Individual articles/provisions within regional instruments |\n"
        "| **International Instruments** | Treaties, conventions, and model laws (e.g. HCCH Principles) |\n"
        "| **International Legal Provisions** | Individual articles/provisions within international instruments |\n"
        "| **Literature** | Academic and practitioner publications on choice of law |\n"
        "| **Arbitral Awards** | Published arbitral awards with choice-of-law analysis |\n"
        "| **Arbitral Rules** | Institutional arbitration rules (e.g. ICC, LCIA) |\n"
        "| **Arbitral Provisions** | Individual articles within arbitral rules |\n"
        "| **Arbitral Institutions** | Arbitration institutions (e.g. ICC, SIAC) |\n"
        "| **Jurisdictions** | Countries and territories with metadata (region, legal family) |\n"
        "| **Specialists** | Choice-of-law experts by jurisdiction |\n\n"
        "Bulk CSV/XLSX exports are also available at "
        "[cold.global/data-sets](https://cold.global/data-sets).\n\n"
        "## Quick start for data scientists\n\n"
        "1. **Search** — `GET /api/v1/search/?search_string=party+autonomy` "
        "returns paginated results across all datasets.\n"
        "2. **Bulk export** — `GET /api/v1/search/full_table?table=Court+Decisions` "
        "returns every record in a table (see table names above).\n"
        "3. **Record detail** — `GET /api/v1/search/details?table=Court+Decisions&id=CD-CHE-42` "
        "returns a single record with its related entities.\n"
        "4. **Entity lists** — `GET /api/v1/entities/court-decisions?jurisdiction=CHE` "
        "returns paginated, filterable entity catalogues.\n"
        "5. **Statistics** — `GET /api/v1/statistics/counts` "
        "returns record counts per entity type, optionally scoped to a jurisdiction.\n\n"
        "## Glossary\n\n"
        "Key private international law terms used throughout the API "
        "(party autonomy, dépeçage, PIL codification, mandatory rules, etc.) "
        "are defined in the [CoLD Glossary](https://cold.global/learn/glossary).\n\n"
        "## Authentication\n\n"
        "**Read-only data endpoints are publicly accessible — no API key or token required.**\n\n"
        "Write endpoints (submitting suggestions, feedback, case analysis) require an Auth0 JWT "
        "in the `Authorization: Bearer <token>` header. "
        "Moderation endpoints additionally require editor or admin roles.\n"
    ),
    contact={
        "name": "CoLD Team — University of Lucerne",
        "url": "https://cold.global",
    },
    license_info={
        "name": "CC BY 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    },
    openapi_tags=[
        {
            "name": "Search",
            "description": (
                "Core data-access endpoints. Full-text search across all datasets with faceted filtering "
                "(by table, jurisdiction, theme), entity detail retrieval by CoLD ID, bulk table export, "
                "and specialist lookup by jurisdiction."
            ),
        },
        {
            "name": "Entities",
            "description": (
                "Paginated entity lists per type (court decisions, instruments, literature, etc.) with "
                "optional jurisdiction and theme filters. Useful for building filtered views or exporting "
                "entity catalogues."
            ),
        },
        {
            "name": "Statistics",
            "description": (
                "Aggregate metrics: record counts per entity type, jurisdiction-level answer coverage "
                "percentages, and per-table jurisdiction breakdowns."
            ),
        },
        {
            "name": "AI",
            "description": (
                "AI-powered helpers. Currently exposes a query classifier that maps free-text questions "
                "to predefined CoLD thematic categories."
            ),
        },
        {
            "name": "Case Analyzer",
            "description": (
                "Multi-step court decision analysis workflow. Upload a PDF, extract text, detect jurisdiction, "
                "and run AI-powered extraction (themes, citations, PIL provisions, etc.). "
                "Results stream as Server-Sent Events. Requires authentication."
            ),
        },
        {
            "name": "LandingPage",
            "description": "Helper endpoints for the CoLD landing page, including jurisdiction data-availability flags.",
        },
        {
            "name": "Sitemap",
            "description": "Returns all indexable frontend URLs for search-engine sitemap generation.",
        },
        {
            "name": "Suggestions",
            "description": (
                "Community data contributions. Authenticated users can submit new court decisions, instruments, "
                "or literature entries for moderator review. Editors/admins manage the moderation queue."
            ),
        },
        {
            "name": "Feedback",
            "description": (
                "Entity-level feedback. Users can report errors or suggest corrections on existing records. "
                "Editors/admins triage and resolve feedback items."
            ),
        },
        {
            "name": "Submarine",
            "description": "Easter egg.",
        },
    ],
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(search.router)
api_router.include_router(ai.router)
api_router.include_router(case_analyzer.router)
api_router.include_router(submarine.router)
api_router.include_router(sitemap.router)
api_router.include_router(landing_page.router)
api_router.include_router(statistics.router)
api_router.include_router(entities.router)

api_router.include_router(suggestions_router.router)
api_router.include_router(feedback.router)


app.include_router(api_router)


@app.get("/api/v1", summary="Health check", description="Returns a simple message confirming the API is running.")
def root():
    return {"message": "Hello World from CoLD"}


# Initialize Logfire with service name for distributed tracing
logfire.configure(
    service_name="backend",
    service_version="1.0.0",
    distributed_tracing=True,
)

# Enable auto-instrumentation
logfire.instrument_fastapi(app)
logfire.instrument_sqlalchemy()
logfire.instrument_requests()
logfire.instrument_openai_agents()


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
