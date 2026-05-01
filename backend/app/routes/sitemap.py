from fastapi import APIRouter, Depends

from app.schemas.responses import SitemapEntry
from app.services.sitemap import SitemapService


def get_sitemap_service() -> SitemapService:
    """Dependency function to lazily instantiate the SitemapService."""
    return SitemapService()


router = APIRouter(prefix="/sitemap", tags=["Sitemap"])


@router.get("/urls")
def get_all_frontend_urls(
    sitemap_service: SitemapService = Depends(get_sitemap_service),
) -> list[SitemapEntry]:
    results = sitemap_service.get_all_frontend_urls()
    return results
