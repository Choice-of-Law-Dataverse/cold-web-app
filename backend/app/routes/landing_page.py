from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.auth import verify_jwt_token
from app.services.landing_page import LandingPageService

# Initialize service
landing_page_service = LandingPageService()

# Define router
router = APIRouter(prefix="/landing-page", tags=["LandingPage"], dependencies=[Depends(verify_jwt_token)])


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
def get_jurisdictions(request: Request):
    """Returns list of Alpha-3 codes with has_data flag (1 or 0) based on Answers table."""
    results = landing_page_service.get_jurisdictions()
    return results


@router.get(
    "/count-by-jurisdiction",
    summary="Count records by jurisdiction for a specific table",
    description=(
        "Returns count of rows grouped by jurisdiction for the specified table. "
        "Supported tables: Court_Decisions, Domestic_Instruments, Literature."
    ),
    responses={
        200: {
            "description": "Array of jurisdictions with their counts.",
            "content": {
                "application/json": {
                    "example": [
                        {"jurisdiction": "United Kingdom", "n": 97},
                        {"jurisdiction": "Australia", "n": 84},
                    ]
                }
            },
        },
        400: {"description": "Invalid table name provided."},
    },
)
def count_by_jurisdiction(
    request: Request,
    table: str = Query(..., description="Table name (e.g., 'Court_Decisions', 'Domestic_Instruments', 'Literature')"),
):
    """Returns count of rows grouped by jurisdiction for the specified table."""
    results = landing_page_service.count_by_jurisdiction(table)
    if results is None or (
        isinstance(results, list)
        and len(results) == 0
        and table not in ["Court_Decisions", "Domestic_Instruments", "Literature"]
    ):
        raise HTTPException(status_code=400, detail=f"Invalid table name: {table}")
    return results
