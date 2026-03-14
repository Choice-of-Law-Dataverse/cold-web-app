from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

from app.services.db_manager import db_manager

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, connection_string: str | None = None, max_retries: int = 3, retry_delay: float = 0.5):
        if not db_manager.is_initialized and connection_string:
            db_manager.initialize(connection_string)

        self.engine = db_manager.get_engine()
        self.metadata: sa.MetaData | None = None
        self._metadata_reflected = False
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _ensure_metadata(self) -> None:
        """Lazily reflect metadata on first use."""
        if self.metadata is None:
            self.metadata = sa.MetaData()

        if not self._metadata_reflected and self.engine and self.metadata is not None:
            try:
                self.metadata.reflect(bind=self.engine)
                self._metadata_reflected = True
            except SQLAlchemyError:
                logger.exception("Error reflecting metadata")
                self.metadata = None

    def _retry_on_empty(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Retry when the database returns empty results, up to max_retries."""
        last_result: Any = None
        for _attempt in range(self.max_retries):
            last_result = func(*args, **kwargs)
            if last_result:
                return last_result
            time.sleep(self.retry_delay)
        return last_result

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]] | None:
        def fetch_query() -> list[dict[str, Any]] | None:
            with db_manager.get_session() as session:
                try:
                    result = session.execute(sa.text(query), params or {})
                    rows = result.fetchall()
                    if not rows:
                        return []

                    columns = result.keys()
                    results = [dict(zip(columns, row, strict=False)) for row in rows]
                    return results

                except SQLAlchemyError:
                    logger.exception("Error executing query")
                    return None

        return self._retry_on_empty(fetch_query)
