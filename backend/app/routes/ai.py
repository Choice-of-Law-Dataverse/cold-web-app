from fastapi import APIRouter, Request, Depends
from app.auth import verify_jwt_token
from app.schemas.requests import ClassifyQueryRequest
from app.services.ai import GPT

ai_router = APIRouter(dependencies=[Depends(verify_jwt_token)])
gpt = GPT()


@ai_router.post("/classify_query")
def classify_query(body: ClassifyQueryRequest):
    query = body.query
    classification = gpt.classify_user_query(query)
    return classification
