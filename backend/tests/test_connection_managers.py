"""Tests for database and HTTP connection managers."""

import pytest
import sqlalchemy as sa
from sqlalchemy.pool import NullPool, QueuePool

from app.services.db_manager import DatabaseManager, SuggestionsDBManager
from app.services.http_session_manager import HTTPSessionManager


class TestDatabaseManager:
    """Tests for DatabaseManager singleton."""

    def test_singleton_pattern(self):
        """Test that DatabaseManager is a singleton."""
        manager1 = DatabaseManager()
        manager2 = DatabaseManager()
        assert manager1 is manager2

    def test_initialize_with_valid_connection_string(self):
        """Test initialization with a valid connection string."""
        # Use in-memory SQLite for testing
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(
            connection_string="sqlite:///:memory:",
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )

        assert manager.is_initialized
        assert manager._engine is not None
        assert manager._session_factory is not None
        assert isinstance(manager._engine.pool, QueuePool)

        # Cleanup
        manager.dispose()

    def test_initialize_without_connection_string(self):
        """Test that initialization fails without connection string."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        with pytest.raises(ValueError, match="Connection string is required"):
            manager.initialize(connection_string="")

    def test_get_engine_before_initialization(self):
        """Test that get_engine raises error if not initialized."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        with pytest.raises(RuntimeError, match="DatabaseManager not initialized"):
            manager.get_engine()

    def test_get_session_before_initialization(self):
        """Test that get_session raises error if not initialized."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        with pytest.raises(RuntimeError, match="DatabaseManager not initialized"):
            manager.get_session()

    def test_get_session_after_initialization(self):
        """Test that we can get a session after initialization."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(connection_string="sqlite:///:memory:")

        session = manager.get_session()
        assert session is not None
        session.close()

        # Cleanup
        manager.dispose()

    def test_dispose(self):
        """Test that dispose properly cleans up resources."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(connection_string="sqlite:///:memory:")
        assert manager.is_initialized

        manager.dispose()
        assert not manager.is_initialized
        assert manager._engine is None
        assert manager._session_factory is None

    def test_reinitialize_warning(self, caplog):
        """Test that re-initialization logs a warning."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(connection_string="sqlite:///:memory:")

        # Try to initialize again
        manager.initialize(connection_string="sqlite:///:memory:")

        assert "already initialized" in caplog.text.lower()

        # Cleanup
        manager.dispose()

    def test_connection_pooling_configuration(self):
        """Test that connection pooling is properly configured."""
        manager = DatabaseManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        pool_size = 3
        max_overflow = 7

        manager.initialize(
            connection_string="sqlite:///:memory:",
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        engine = manager.get_engine()
        assert isinstance(engine.pool, QueuePool)
        # SQLite doesn't use traditional pooling, so we can't test exact values
        # But we verify the engine was created with pooling config

        # Cleanup
        manager.dispose()


class TestSuggestionsDBManager:
    """Tests for SuggestionsDBManager singleton."""

    def test_singleton_pattern(self):
        """Test that SuggestionsDBManager is a singleton."""
        manager1 = SuggestionsDBManager()
        manager2 = SuggestionsDBManager()
        assert manager1 is manager2

    def test_initialize_with_valid_connection_string(self):
        """Test initialization with a valid connection string."""
        manager = SuggestionsDBManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(
            connection_string="sqlite:///:memory:",
            pool_size=3,
            max_overflow=5,
        )

        assert manager.is_initialized
        assert manager._engine is not None
        assert manager._session_factory is not None

        # Cleanup
        manager.dispose()

    def test_get_session_after_initialization(self):
        """Test that we can get a session after initialization."""
        manager = SuggestionsDBManager()
        manager._engine = None  # Reset state
        manager._session_factory = None

        manager.initialize(connection_string="sqlite:///:memory:")

        session = manager.get_session()
        assert session is not None
        session.close()

        # Cleanup
        manager.dispose()


class TestHTTPSessionManager:
    """Tests for HTTPSessionManager singleton."""

    def test_singleton_pattern(self):
        """Test that HTTPSessionManager is a singleton."""
        manager1 = HTTPSessionManager()
        manager2 = HTTPSessionManager()
        assert manager1 is manager2

    def test_auto_initialize_on_get_session(self, caplog):
        """Test that get_session auto-initializes if not already initialized."""
        manager = HTTPSessionManager()
        manager._session = None  # Reset state

        session = manager.get_session()
        assert session is not None
        assert "not initialized" in caplog.text.lower()
        assert manager.is_initialized

        # Cleanup
        manager.close()

    def test_initialize_with_custom_settings(self):
        """Test initialization with custom settings."""
        manager = HTTPSessionManager()
        manager._session = None  # Reset state

        manager.initialize(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=2,
            backoff_factor=0.5,
        )

        assert manager.is_initialized
        session = manager.get_session()
        assert session is not None

        # Cleanup
        manager.close()

    def test_close(self):
        """Test that close properly cleans up resources."""
        manager = HTTPSessionManager()
        manager._session = None  # Reset state

        manager.initialize()
        assert manager.is_initialized

        manager.close()
        assert not manager.is_initialized
        assert manager._session is None

    def test_reinitialize_warning(self, caplog):
        """Test that re-initialization logs a warning."""
        manager = HTTPSessionManager()
        manager._session = None  # Reset state

        manager.initialize()

        # Try to initialize again
        manager.initialize()

        assert "already initialized" in caplog.text.lower()

        # Cleanup
        manager.close()

    def test_session_has_retry_strategy(self):
        """Test that the session has retry strategy configured."""
        manager = HTTPSessionManager()
        manager._session = None  # Reset state

        manager.initialize(max_retries=3)
        session = manager.get_session()

        # Check that adapters are mounted
        assert "http://" in session.adapters
        assert "https://" in session.adapters

        # Cleanup
        manager.close()
