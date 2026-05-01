from fastapi import APIRouter, Depends

from app.schemas.responses import LandingPageJurisdiction
from app.services.landing_page import LandingPageService


def get_landing_page_service() -> LandingPageService:
    """Dependency function to lazily instantiate the LandingPageService."""
    return LandingPageService()


router = APIRouter(prefix="/landing-page", tags=["LandingPage"])


@router.get(
    "/jurisdictions",
    summary="Jurisdictions with data availability",
    description=("Returns ISO Alpha-3 codes and a has_data flag (1/0) depending on whether non-'No data' answers exist."),
    responses={
        200: {
            "description": "Array of jurisdictions and availability flag.",
            "content": {"application/json": {"example": [{"code": "CHE", "has_data": 1}]}},
        }
    },
)
def get_jurisdictions(
    landing_page_service: LandingPageService = Depends(get_landing_page_service),
) -> list[LandingPageJurisdiction]:
    results = landing_page_service.get_jurisdictions()
    return [LandingPageJurisdiction(**r) for r in results]
