from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_jwt_token
from app.routes import ai, search, submarine, user, sitemap, landing_page
from app.services.query_logging import log_query

app = FastAPI(
    title="CoLD API",
    description="""
    # CoLD API Documentation
    This API provides access to the database of the Choice of Law Dataverse (CoLD).
    The CoLD is a research project at the University of Lucerne that collects and analyzes data on choice of law in international contracts.

    The API allows users to query the data, with a full text search feature as the core data retrieval method.
    Other features include fetching all data from specific tables and filtering for specific entries.
    The API also supports JWT authentication for secure access.
    """,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
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
    return {"message": "Hello World from CoLD"}
