import logging
from datetime import date
from pathlib import Path

from app.config import config
from app.services.database import Database

logger = logging.getLogger(__name__)


class SitemapService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
        # Map NocoDB table names to frontend URL prefixes
        self.table_url_mapping = {
            "Answers": "question",
            "Literature": "literature",
            "Regional_Instruments": "regional-instrument",
            "International_Instruments": "international-instrument",
            "Court_Decisions": "court-decision",
            "Domestic_Instruments": "domestic-instrument",
        }

    def get_all_frontend_urls(self):
        """
        Return a list of sitemap entries for dynamic and static frontend routes.
        Each entry is a dict with 'loc' and 'lastmod' (ISO date).
        """
        entries = []
        # Dynamic entries from database tables
        for table_name, prefix in self.table_url_mapping.items():
            try:
                ids = self._get_table_ids(table_name)
                for id_val in ids:
                    entries.append(
                        {
                            "loc": f"/{prefix}/{id_val}",
                            "lastmod": date.today().isoformat(),
                        }
                    )
            except Exception as e:
                logger.warning("Error processing table %s: %s", table_name.strip(), str(e).strip())
        # Static entries from frontend/pages
        try:
            static_paths = self._get_static_paths()
            for route in static_paths:
                entries.append({"loc": route, "lastmod": date.today().isoformat()})
        except Exception as e:
            logger.warning("Error scanning static pages: %s", str(e).strip())
        return entries

    def _get_table_ids(self, table_name):
        """
        Retrieve all non-null IDs from the given NocoDB table.
        """
        try:
            query = f'SELECT id FROM "{config.NOCODB_POSTGRES_SCHEMA}"."{table_name}" WHERE id IS NOT NULL ORDER BY id'
            result = self.db.execute_query(query)
            ids = []
            for row in result or []:
                if "id" in row and row["id"]:
                    ids.append(row["id"])
            return ids
        except Exception as e:
            logger.warning("Error getting IDs from table %s: %s", table_name.strip(), str(e).strip())
            return []

    def _get_static_paths(self):
        """
        Scan the frontend/pages directory to generate static route paths.
        """
        paths = []
        project_root = Path(__file__).resolve().parents[4]
        pages_dir = project_root / "frontend" / "pages"
        for vue_file in pages_dir.rglob("*.vue"):
            parts = vue_file.relative_to(pages_dir).with_suffix("").parts
            # Skip dynamic routes
            if any(part.startswith("[") for part in parts):
                continue
            # Build route
            if parts[-1] == "index":
                route = "/" + "/".join(parts[:-1])
            else:
                route = "/" + "/".join(parts)
            # Normalize
            if route.endswith("/") and route != "/":
                route = route[:-1]
            paths.append(route or "/")
        return sorted(set(paths))
