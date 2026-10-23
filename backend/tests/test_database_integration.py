"""Tests for Database query execution against the lifespan-owned pool."""

import time

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.services.database import Database
from app.services.db_manager import db_manager


class TestDatabaseWithManager:
    """Tests for Database class integration with DatabaseManager."""

    def setup_method(self):
        db_manager._engine = None
        db_manager._session_factory = None

    def teardown_method(self):
        db_manager.dispose()

    def test_construction_does_not_initialize_the_pool(self):
        """The application lifespan owns pool initialization, not Database."""
        Database()

        assert not db_manager.is_initialized

    def test_query_without_initialized_pool_raises(self):
        with pytest.raises(RuntimeError, match="not initialized"):
            Database().execute_query("SELECT 1")

    def test_execute_query_returns_rows_as_dicts(self):
        db_manager.initialize("sqlite:///:memory:")
        with db_manager.get_session() as session:
            session.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"))
            session.execute(text("INSERT INTO test_table (id, name) VALUES (1, 'test')"))
            session.commit()

        results = Database().execute_query("SELECT * FROM test_table")

        assert results == [{"id": 1, "name": "test"}]

    def test_empty_result_returns_immediately(self):
        db_manager.initialize("sqlite:///:memory:")
        with db_manager.get_session() as session:
            session.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"))
            session.commit()

        started = time.monotonic()
        results = Database().execute_query("SELECT * FROM test_table WHERE id = :id", {"id": 999})

        assert results == []
        assert time.monotonic() - started < 0.4

    def test_query_error_propagates(self):
        db_manager.initialize("sqlite:///:memory:")

        with pytest.raises(SQLAlchemyError):
            Database().execute_query("SELECT * FROM missing_table")
