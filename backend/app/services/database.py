from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable
from typing import Any

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, connection_string, max_retries=3, retry_delay=0.5):
        """
        Initialize the database module.

        Parameters:
        - connection_string: Database connection string.
        - max_retries: Maximum number of retries for fetching data.
        - retry_delay: Delay between retries in seconds.
        """
        self.engine = sa.create_engine(connection_string)
        self.metadata: sa.MetaData | None = sa.MetaData()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        metadata = self.metadata
        assert metadata is not None
        try:
            metadata.reflect(bind=self.engine)
        except SQLAlchemyError as e:
            logger.exception("Error reflecting metadata: %s", str(e).strip())
            self.metadata = None

        self.Session = sessionmaker(bind=self.engine)

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

    def get_all_entries(self):
        metadata = self.metadata
        if metadata is None:
            return None

        def fetch_all_entries() -> dict[str, list[dict[str, Any]]]:
            all_entries: dict[str, list[dict[str, Any]]] = {}
            with self.Session() as session:
                try:
                    for table_name, table in metadata.tables.items():
                        query = table.select()
                        result = session.execute(query)
                        columns = result.keys()
                        entries = [dict(zip(columns, row, strict=False)) for row in result.fetchall()]
                        all_entries[table_name] = entries
                except SQLAlchemyError as e:
                    logger.exception("Error getting all entries: %s", str(e).strip())
            return all_entries

        return self._retry_on_empty(fetch_all_entries)

    def get_entries_from_tables(self, list_of_tables: Iterable[str]):
        metadata = self.metadata
        if metadata is None:
            return None

        def fetch_entries() -> dict[str, list[dict[str, Any]]]:
            entries_from_tables: dict[str, list[dict[str, Any]]] = {}
            with self.Session() as session:
                try:
                    for table_name in list_of_tables:
                        if table_name in metadata.tables:
                            table = metadata.tables[table_name]
                            query = table.select()
                            result = session.execute(query)
                            columns = result.keys()
                            entries = [dict(zip(columns, row, strict=False)) for row in result.fetchall()]
                            entries_from_tables[table_name] = entries
                        else:
                            logger.warning("Table %s does not exist in the database", table_name.strip())
                except SQLAlchemyError as e:
                    logger.exception("Error getting entries from tables: %s", str(e).strip())
            return entries_from_tables

        return self._retry_on_empty(fetch_entries)

    def get_entry_by_id(self, table_name: str, entry_id: Any):
        metadata = self.metadata
        if metadata is None:
            return None

        id_columns = {
            "Answers": "ID",
            "HCCH Answers": "ID",
            "Domestic Instruments": "ID",
            "Domestic Legal Provisions": "Name",
            "Regional Instruments": "ID",
            "Regional Legal Provisions": "ID",
            "International Instruments": "ID",
            "International Legal Provisions": "ID",
            "Court Decisions": "ID",
            "Jurisdictions": "Alpha-3 Code",
            "Literature": "ID",
        }

        def fetch_entry() -> dict[str, Any]:
            entry: dict[str, Any] = {}
            with self.Session() as session:
                try:
                    if table_name in metadata.tables:
                        table = metadata.tables[table_name]
                        if table_name in id_columns:
                            id_column = id_columns[table_name]
                            query = table.select().where(table.c[id_column] == entry_id)
                            result = session.execute(query)

                            row = result.fetchone()
                            if row:
                                columns = result.keys()
                                entry = dict(zip(columns, row, strict=False))
                            else:
                                logger.warning("No entry found with id %s in table %s", str(entry_id).strip(), table_name.strip())
                                return {"error": "no entry found with the specified id"}
                        else:
                            logger.warning("Table %s does not have a mapped id column", table_name.strip())
                    else:
                        logger.warning("Table %s does not exist in the database", table_name.strip())
                except SQLAlchemyError as e:
                    logger.exception("Error getting entry by id: %s", str(e).strip())
            return entry

        return self._retry_on_empty(fetch_entry)

    def execute_query(self, query: str, params: dict[str, Any] | None = None):
        def fetch_query() -> list[dict[str, Any]] | None:
            with self.Session() as session:
                try:
                    result = session.execute(sa.text(query), params or {})
                    rows = result.fetchall()
                    if not rows:
                        return []

                    columns = result.keys()
                    results = [dict(zip(columns, row, strict=False)) for row in rows]
                    return results

                except SQLAlchemyError as e:
                    logger.exception("Error executing query: %s", str(e).strip())
                    return None

        return self._retry_on_empty(fetch_query)
