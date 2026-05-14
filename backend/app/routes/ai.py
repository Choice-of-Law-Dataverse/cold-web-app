from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import verify_frontend_request
from app.services.ai import QueryClassifier


def get_query_classifier() -> QueryClassifier:
    return QueryClassifier()


router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(verify_frontend_request)])


_CLASSIFY_QUERY_DESCRIPTION = (
    "Maps a free-text question to the most relevant predefined CoLD thematic category "
    "(e.g. 'Party autonomy (concept)', 'Mandatory rules', 'Renvoi'). "
    "Uses an LLM under the hood. The returned string can be fed back into the search "
    "endpoint's `themes` filter to retrieve matching records."
)
_CLASSIFY_QUERY_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "The matched CoLD category as a plain string.",
        "content": {"application/json": {"example": "Party autonomy (concept)"}},
    },
    502: {"description": "The upstream AI service returned an error or timed out."},
}


@router.get(
    "/classify_query",
    summary="Classify a free-text user query into a predefined category",
    description=_CLASSIFY_QUERY_DESCRIPTION,
    responses=_CLASSIFY_QUERY_RESPONSES,
)
def classify_query_get(
    query: Annotated[str, Query(description="Free-text query to classify, e.g. 'How do courts treat party autonomy?'")],
    classifier: QueryClassifier = Depends(get_query_classifier),
) -> str:
    classification = classifier.classify_user_query(query)
    if isinstance(classification, dict):
        raise HTTPException(status_code=502, detail=classification.get("error", "Upstream AI service error"))
    return classification
