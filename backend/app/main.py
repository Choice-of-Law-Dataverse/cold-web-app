from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_jwt_token
from app.routes import ai, search, user
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

app.include_router(search.router)
app.include_router(user.router)
app.include_router(ai.router)


@app.get("/", dependencies=[Depends(verify_jwt_token)])
def root():
    return {"message": "Hello World from CoLD"}
