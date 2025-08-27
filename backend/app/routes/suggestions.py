from fastapi import APIRouter, Depends, Request, Header, HTTPException, status
from typing import Optional
from app.auth import verify_jwt_token
from app.schemas.suggestions import (
    SuggestionPayload,
    SuggestionResponse,
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    RegionalInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
)
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
        payload = {
            **body.data,
            **({"submitter_email": body.submitter_email} if body.submitter_email else {}),
            **({"submitter_comments": body.submitter_comments} if body.submitter_comments else {}),
        }
        new_id = service.save_suggestion(
            payload=payload,
            table="generic",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=body.source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/court-decisions",
    summary="Submit a new Court Decision suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_court_decision(
    body: CourtDecisionSuggestion,
    request: Request,
    authorization: str = Header(None),
    source: Optional[str] = Header(None),
):
    try:
        payload = {"category": "court_decision", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="court_decisions",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/domestic-instruments",
    summary="Submit a new Domestic Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_domestic_instrument(
    body: DomesticInstrumentSuggestion,
    request: Request,
    authorization: str = Header(None),
    source: Optional[str] = Header(None),
):
    try:
        payload = {"category": "domestic_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="domestic_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/regional-instruments",
    summary="Submit a new Regional Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_regional_instrument(
    body: RegionalInstrumentSuggestion,
    request: Request,
    authorization: str = Header(None),
    source: Optional[str] = Header(None),
):
    try:
        payload = {"category": "regional_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="regional_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/international-instruments",
    summary="Submit a new International Instrument suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_international_instrument(
    body: InternationalInstrumentSuggestion,
    request: Request,
    authorization: str = Header(None),
    source: Optional[str] = Header(None),
):
    try:
        payload = {"category": "international_instrument", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="international_instruments",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/literature",
    summary="Submit a new Literature suggestion",
    response_model=SuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_literature(
    body: LiteratureSuggestion,
    request: Request,
    authorization: str = Header(None),
    source: Optional[str] = Header(None),
):
    try:
        payload = {"category": "literature", **body.model_dump()}
        new_id = service.save_suggestion(
            payload=payload,
            table="literature",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            source=source,
            authorization=authorization,
        )
        return SuggestionResponse(id=new_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
