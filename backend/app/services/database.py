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
    def __init__(self, connection_string=None, max_retries=3, retry_delay=0.5):
        """
        Initialize the database module using the singleton DatabaseManager.

        Parameters:
        - connection_string: Database connection string (deprecated, uses singleton manager).
        - max_retries: Maximum number of retries for fetching data.
        - retry_delay: Delay between retries in seconds.
        """
        # Use the singleton database manager
        if not db_manager.is_initialized and connection_string:
            db_manager.initialize(connection_string)

        self.engine = db_manager.get_engine()
        self.metadata: sa.MetaData | None = sa.MetaData()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        metadata = self.metadata
        assert metadata is not None
        try:
            metadata.reflect(bind=self.engine)
        except SQLAlchemyError:
            logger.exception("Error reflecting metadata")
            self.metadata = None

    def _retry_on_empty(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Retry logic to handle cases where the database returns empty results.

        Parameters:
        - func: Function to call for fetching data.
        - args, kwargs: Arguments to pass to the function.

        Returns:
        - The result from the function or an empty list if retries are exhausted.
        """
        last_result: Any = None
        for _attempt in range(self.max_retries):
            last_result = func(*args, **kwargs)
            if last_result:  # If data is found, return immediately
                return last_result
            time.sleep(self.retry_delay)  # Wait before retrying
        return last_result  # Return the final result after all retries

    def execute_query(self, query: str, params: dict[str, Any] | None = None):
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
