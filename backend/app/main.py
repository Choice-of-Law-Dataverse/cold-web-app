from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_jwt_token
from app.routes.search import search_router
from app.routes.user import user_router
from app.routes.ai import ai_router
from app.config import config

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])

@app.get("/", dependencies=[Depends(verify_jwt_token)])
def root():
    return {"message": "Hello World from CoLD"}