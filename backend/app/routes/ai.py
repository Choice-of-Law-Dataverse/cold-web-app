from fastapi import APIRouter, Request, Depends
from app.auth import verify_jwt_token
from app.schemas.requests import ClassifyQueryRequest
from app.services.ai import GPT
from app.auth import verify_jwt_token

gpt = GPT()

router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(verify_jwt_token)])


@router.post(
    "/classify_query",
    summary="Classify a free-text user query into a predefined category",
    description=(
        "Uses an external model to classify the user's query into one of the predefined CoLD categories."
    ),
    responses={
        200: {
            "description": "Classification result",
            "content": {
                "application/json": {
                    "example": "Party autonomy (concept)"
                }
            },
        },
        502: {"description": "Upstream AI service error."},
    },
)
def classify_query(body: ClassifyQueryRequest):
    query = body.query
    classification = gpt.classify_user_query(query)
    return classification
