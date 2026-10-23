from __future__ import annotations

from typing import Any

import sqlalchemy as sa

from app.services.db_manager import db_manager


class Database:
    """Runs SQL against the main database pool, which the application lifespan owns.

    An empty result is returned as an empty list; any database error propagates as a
    `sqlalchemy.exc.SQLAlchemyError` so callers can tell "no rows" from "query failed".
    """

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with db_manager.get_session() as session:
            result = session.execute(sa.text(query), params or {})
            return [dict(row) for row in result.mappings()]
