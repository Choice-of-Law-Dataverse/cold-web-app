from fastapi import APIRouter, Depends

from app.auth import verify_frontend_request
from app.services.sitemap import SitemapService


def get_sitemap_service() -> SitemapService:
    """Dependency function to lazily instantiate the SitemapService."""
    return SitemapService()


router = APIRouter(prefix="/sitemap", tags=["Sitemap"], dependencies=[Depends(verify_frontend_request)])


@router.get("/urls")
def get_all_frontend_urls(
    sitemap_service: SitemapService = Depends(get_sitemap_service),
):
    """
    Get all possible frontend URLs for the CoLD application.
    Returns URLs for all questions, literature, regional instruments,
    international instruments, court decisions, and domestic instruments.
    """
    results = sitemap_service.get_all_frontend_urls()
    return results
