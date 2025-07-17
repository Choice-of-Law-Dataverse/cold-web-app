from fastapi import APIRouter, Depends, Request
from app.services.landing_page import LandingPageService
from app.auth import verify_jwt_token

# Initialize service
landing_page_service = LandingPageService()

# Define router
router = APIRouter(
    prefix="/landing-page",
    tags=["LandingPage"],
    dependencies=[Depends(verify_jwt_token)]
)

@router.get("/jurisdictions")
def get_jurisdictions(request: Request):
    """
    Returns list of Alpha-3 codes with has_data flag (1 or 0) based on Answers table.
    """
    results = landing_page_service.get_jurisdictions()
    return results
