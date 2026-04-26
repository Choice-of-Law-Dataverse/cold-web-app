from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import verify_frontend_request
from app.schemas.requests import ClassifyQueryRequest
from app.services.ai import QueryClassifier


def get_query_classifier() -> QueryClassifier:
    return QueryClassifier()


router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(verify_frontend_request)])


_CLASSIFY_QUERY_DESCRIPTION = "Uses an external model to classify the user's query into one of the predefined CoLD categories."
_CLASSIFY_QUERY_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Classification result",
        "content": {"application/json": {"example": "Party autonomy (concept)"}},
    },
    502: {"description": "Upstream AI service error."},
}


def _do_classify_query(query: str, classifier: QueryClassifier) -> str:
    classification = classifier.classify_user_query(query)
    if isinstance(classification, dict):
        raise HTTPException(status_code=502, detail=classification.get("error", "Upstream AI service error"))
    return classification


@router.post(
    "/classify_query",
    summary="Classify a free-text user query into a predefined category",
    description=_CLASSIFY_QUERY_DESCRIPTION,
    responses=_CLASSIFY_QUERY_RESPONSES,
)
def classify_query(
    body: ClassifyQueryRequest,
    classifier: QueryClassifier = Depends(get_query_classifier),
) -> str:
    return _do_classify_query(body.query, classifier)


@router.get(
    "/classify_query",
    summary="Classify a free-text user query (GET alternative)",
    description=_CLASSIFY_QUERY_DESCRIPTION,
    responses=_CLASSIFY_QUERY_RESPONSES,
)
def classify_query_get(
    query: Annotated[str, Query(description="Free-text query to classify, e.g. 'How do courts treat party autonomy?'")],
    classifier: QueryClassifier = Depends(get_query_classifier),
) -> str:
    return _do_classify_query(query, classifier)
