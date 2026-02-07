from fastapi import APIRouter, Depends

from app.auth import verify_frontend_request
from app.schemas.requests import ClassifyQueryRequest
from app.services.ai import GPT


def get_gpt() -> GPT:
    """Dependency function to lazily instantiate the GPT service."""
    return GPT()


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
    gpt: GPT = Depends(get_gpt),
):
    query = body.query
    classification = gpt.classify_user_query(query)
    return classification
