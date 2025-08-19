from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_jwt_token
from app.routes import ai, search, submarine, user, sitemap, landing_page
from app.services.query_logging import log_query

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
    """,
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
            "name": "Sitemap",
            "description": "Frontend URLs for site map generation.",
        },
        {
            "name": "LandingPage",
            "description": "Landing page support endpoints (e.g., jurisdictions with data).",
        },
        {
            "name": "Submarine",
            "description": "Fun demo route.",
        },
    ],
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
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
# api_router.include_router(user.router)
api_router.include_router(ai.router)
api_router.include_router(submarine.router)
api_router.include_router(sitemap.router)
api_router.include_router(landing_page.router)

app.include_router(api_router)

@app.get("/api/v1")
def root():
    """Simple health check endpoint for the CoLD API root."""
    return {"message": "Hello World from CoLD"}
