from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_jwt_token
from app.routes import ai, search, submarine, user, sitemap, landing_page
from app.services.query_logging import log_query

app = FastAPI(
    title="CoLD API",
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
