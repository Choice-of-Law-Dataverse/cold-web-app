from fastapi import APIRouter, Depends, Request

from app.auth import verify_jwt_token
from app.services.sitemap import SitemapService

sitemap_service = SitemapService()

router = APIRouter(prefix="/sitemap", tags=["Sitemap"], dependencies=[Depends(verify_jwt_token)])


@router.get("/urls")
def get_all_frontend_urls(request: Request):
    """
    Get all possible frontend URLs for the CoLD application.
    Returns URLs for all questions, literature, regional instruments,
    international instruments, court decisions, and domestic instruments.
    """
    results = sitemap_service.get_all_frontend_urls()
    return results
