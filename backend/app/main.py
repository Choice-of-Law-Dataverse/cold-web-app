import logging
from contextlib import asynccontextmanager

import logfire
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.routes import (
    ai,
    case_analysis,
    landing_page,
    search,
    sitemap,
    statistics,
    submarine,
    suggestions as suggestions_router,
)
from app.services.db_manager import db_manager, suggestions_db_manager
from app.services.http_session_manager import http_session_manager
from app.services.query_logging import log_query

# Configure logging level
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    logger = logging.getLogger(__name__)

    # Startup
    logger.info("Initializing connection pools...")

    # Initialize main database connection pool
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

    # Initialize suggestions database connection pool
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

    # Initialize HTTP session manager for NocoDB API calls
    http_session_manager.initialize(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=3,
    )
    logger.info("HTTP session manager initialized")

    logger.info("All connection pools initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down connection pools...")

    # Dispose database connection pools
    db_manager.dispose()
    suggestions_db_manager.dispose()

    # Close HTTP session
    http_session_manager.close()

    logger.info("Connection pools shut down successfully")


app = FastAPI(
    title="CoLD API",
    version="1.0.0",
    description="""
    # CoLD API Documentation
    The Choice of Law Dataverse (CoLD) API provides programmatic access to a curated knowledge base on choice of law in international contracts.

    Core capabilities:
    - Full-text search across all data domains with filtering and sorting by date.
    - Fetch curated details for a specific record by CoLD ID, including first-hop related entries.
    - Retrieve full tables or filtered subsets using user-facing fields (mapping-aware).
    - Site map and landing page helper endpoints for the frontend.

    Authentication:
    - All endpoints (except the root) require a Bearer JWT in the `Authorization` header: `Authorization: Bearer <token>`.
    """,  # noqa: E501
    contact={
        "name": "CoLD Team",
        "url": "https://choice-of-law-dataverse.org/",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Search",
            "description": "Full text search, curated details, and full/filtered table retrieval.",
        },
        {
            "name": "AI",
            "description": "AI helpers such as query classification.",
        },
        {
            "name": "Case Analysis",
            "description": "Court decision analysis with AI-powered extraction and classification.",
        },
        {
            "name": "Sitemap",
            "description": "Frontend URLs for site map generation.",
        },
        {
            "name": "LandingPage",
            "description": "Landing page support endpoints (e.g., jurisdictions with data).",
        },
        {
            "name": "Statistics",
            "description": "Data aggregation and statistics endpoints.",
        },
        {
            "name": "Submarine",
            "description": "Fun demo route.",
        },
        {
            "name": "Suggestions",
            "description": "User-submitted data suggestions storage.",
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

app.middleware("http")(log_query)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(search.router)
api_router.include_router(ai.router)
api_router.include_router(case_analysis.router)
api_router.include_router(submarine.router)
api_router.include_router(sitemap.router)
api_router.include_router(landing_page.router)
api_router.include_router(statistics.router)

api_router.include_router(suggestions_router.router)


app.include_router(api_router)


@app.get("/api/v1")
def root():
    """Simple health check endpoint for the CoLD API root."""
    return {"message": "Hello World from CoLD"}


# Initialize Logfire with service name for distributed tracing
logfire.configure(
    service_name="backend",
    service_version="1.0.0",
)

# Enable auto-instrumentation
logfire.instrument_fastapi(app)
logfire.instrument_sqlalchemy()
logfire.instrument_requests()
logfire.instrument_pymongo()


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
