from fastapi import APIRouter, Depends, Request, Header, HTTPException, status
from app.auth import verify_jwt_token
from app.schemas.suggestions import SuggestionPayload, SuggestionResponse
from app.services.suggestions import SuggestionService

router = APIRouter(
    prefix="/suggestions",
    tags=["Suggestions"],
    dependencies=[Depends(verify_jwt_token)],
)

service = SuggestionService()


@router.post(
    "/",
    summary="Submit a new data suggestion",
    description=(
        "Accepts arbitrary dictionaries from the frontend and stores them in a separate Postgres table."
    ),
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_suggestion(
    body: SuggestionPayload,
    request: Request,
    authorization: str = Header(None),
):
    try:
        new_id = service.save_suggestion(
            payload=body.data,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=body.source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
