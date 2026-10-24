import logging
from contextlib import asynccontextmanager
from importlib.metadata import version as package_version

import logfire
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import openapi
from app.config import config
from app.routes import (
    ai,
    case_analyzer,
    entities,
    feedback,
    landing_page,
    search,
    statistics,
    submarine,
    suggestions as suggestions_router,
)
from app.services.db_manager import db_manager, suggestions_db_manager
from app.services.http_session_manager import http_session_manager

APP_VERSION = package_version("backend")

# Configure logging to send to Logfire
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()), handlers=[logfire.LogfireLoggingHandler()])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    logger = logging.getLogger(__name__)

    with logfire.span("application_startup"):
        logger.info("Initializing connection pools...")

        if config.SQL_CONN_STRING:
            db_manager.initialize(config.SQL_CONN_STRING)
            logger.info("Main database connection pool initialized")
        else:
            logger.warning("SQL_CONN_STRING not configured, database operations will fail")

        suggestions_conn = config.SUGGESTIONS_SQL_CONN_STRING or config.SQL_CONN_STRING
        if suggestions_conn:
            suggestions_db_manager.initialize(suggestions_conn)
            logger.info("Suggestions database connection pool initialized")

        http_session_manager.initialize()
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
    title=openapi.TITLE,
    version=APP_VERSION,
    description=openapi.DESCRIPTION,
    contact=openapi.CONTACT,
    license_info=openapi.LICENSE_INFO,
    openapi_tags=openapi.TAGS,
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
    service_version=APP_VERSION,
    distributed_tracing=True,
    token=config.LOGFIRE_TOKEN,
    send_to_logfire="if-token-present",
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
