from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_frontend_request
from app.schemas.requests import ClassifyQueryRequest
from app.services.ai import QueryClassifier


def get_query_classifier() -> QueryClassifier:
    return QueryClassifier()


router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(verify_frontend_request)])


@router.post(
    "/classify_query",
    summary="Classify a free-text user query into a predefined category",
    description=("Uses an external model to classify the user's query into one of the predefined CoLD categories."),
    responses={
        200: {
            "description": "Classification result",
            "content": {"application/json": {"example": "Party autonomy (concept)"}},
        },
        502: {"description": "Upstream AI service error."},
    },
)
def classify_query(
    body: ClassifyQueryRequest,
    classifier: QueryClassifier = Depends(get_query_classifier),
) -> str:
    query = body.query
    classification = classifier.classify_user_query(query)
    if isinstance(classification, dict):
        raise HTTPException(status_code=502, detail=classification.get("error", "Upstream AI service error"))
    return classification
