"""Tests for Database class with singleton manager integration."""


from app.services.database import Database
from app.services.db_manager import db_manager


class TestDatabaseWithManager:
    """Tests for Database class integration with DatabaseManager."""

    def setup_method(self):
        """Setup test fixtures."""
        # Reset the singleton state before each test
        db_manager._engine = None
        db_manager._session_factory = None

    def teardown_method(self):
        """Cleanup after each test."""
        db_manager.dispose()

    def test_database_initializes_manager_on_first_use(self):
        """Test that Database initializes the manager on first use."""
        assert not db_manager.is_initialized

        # Creating a Database instance should initialize the manager
        db = Database(connection_string="sqlite:///:memory:")

        assert db_manager.is_initialized
        assert db.engine is not None

    def test_database_reuses_existing_manager(self):
        """Test that multiple Database instances reuse the same manager."""
        db1 = Database(connection_string="sqlite:///:memory:")
        engine1 = db1.engine

        # Second instance should use the same engine
        db2 = Database(connection_string="sqlite:///:memory:")
        engine2 = db2.engine

        assert engine1 is engine2

    def test_database_with_invalid_connection_string(self):
        """Test Database initialization with invalid connection string."""
        # This should fail when trying to reflect metadata
        db = Database(connection_string="sqlite:///invalid_path_that_does_not_exist.db")

        # The engine should still be created, but metadata might be None
        assert db.engine is not None

    def test_execute_query_with_manager(self):
        """Test that execute_query uses the manager's session."""
        db = Database(connection_string="sqlite:///:memory:")

        # Create a simple table
        with db_manager.get_session() as session:
            session.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            session.execute("INSERT INTO test_table (id, name) VALUES (1, 'test')")
            session.commit()

        # Query using Database.execute_query
        results = db.execute_query("SELECT * FROM test_table")

        assert results is not None
        assert len(results) == 1
        assert results[0]["name"] == "test"

    def test_database_retry_logic(self):
        """Test that retry logic works correctly."""
        db = Database(connection_string="sqlite:///:memory:", max_retries=2, retry_delay=0.1)

        # Create a simple table
        with db_manager.get_session() as session:
            session.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            session.commit()

        # First attempt returns empty, but should still return empty list (not retry indefinitely)
        results = db.execute_query("SELECT * FROM test_table WHERE id = 999")

        # Should return empty list, not None
        assert results == []

    def test_metadata_reflection_with_manager(self):
        """Test that metadata reflection works with the manager."""
        Database(connection_string="sqlite:///:memory:")

        # Create a table
        with db_manager.get_session() as session:
            session.execute("CREATE TABLE reflected_table (id INTEGER PRIMARY KEY, data TEXT)")
            session.commit()

        # Create a new Database instance to trigger reflection
        db2 = Database(connection_string="sqlite:///:memory:")

        # Metadata should be initialized (even if empty for in-memory SQLite)
        assert db2.metadata is not None

    def test_database_handles_session_context_manager(self):
        """Test that Database methods use session context managers correctly."""
        db = Database(connection_string="sqlite:///:memory:")

        # Create and populate a table
        with db_manager.get_session() as session:
            session.execute("CREATE TABLE context_test (id INTEGER PRIMARY KEY, value TEXT)")
            session.execute("INSERT INTO context_test (id, value) VALUES (1, 'test1')")
            session.execute("INSERT INTO context_test (id, value) VALUES (2, 'test2')")
            session.commit()

        # Use execute_query which internally uses context manager
        results = db.execute_query("SELECT COUNT(*) as count FROM context_test")

        assert results is not None
        assert results[0]["count"] == 2
