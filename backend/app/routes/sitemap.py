from fastapi import APIRouter, Depends

from app.schemas.responses import SitemapEntry
from app.services.sitemap import SitemapService


def get_sitemap_service() -> SitemapService:
    return SitemapService()


router = APIRouter(prefix="/sitemap", tags=["Sitemap"])


@router.get(
    "/urls",
    summary="List all indexable frontend URLs",
    description=(
        "Returns every public-facing URL for the CoLD frontend. "
        "Intended for generating XML sitemaps for search engine indexing."
    ),
    responses={
        200: {
            "description": "Array of URL entries with loc and optional lastmod/priority.",
        }
    },
)
def get_all_frontend_urls(
    sitemap_service: SitemapService = Depends(get_sitemap_service),
) -> list[SitemapEntry]:
    results = sitemap_service.get_all_frontend_urls()
    return results
