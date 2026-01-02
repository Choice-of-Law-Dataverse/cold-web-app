from fastapi import APIRouter, Depends

from app.auth import verify_frontend_request
from app.services.landing_page import LandingPageService

# Initialize service
landing_page_service = LandingPageService()

# Define router
router = APIRouter(prefix="/landing-page", tags=["LandingPage"], dependencies=[Depends(verify_frontend_request)])


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
def get_jurisdictions():
    """Returns list of Alpha-3 codes with has_data flag (1 or 0) based on Answers table."""
    results = landing_page_service.get_jurisdictions()
    return results
