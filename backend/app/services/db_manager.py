"""Database connection manager with connection pooling best practices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton database connection manager with proper pooling configuration."""

    _instance: DatabaseManager | None = None
    _engine: Engine | None = None
    _session_factory: sessionmaker[Session] | None = None

    def __new__(cls) -> DatabaseManager:
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        connection_string: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ) -> None:
        """
        Initialize the database connection pool.

        Parameters:
        - connection_string: Database connection string
        - pool_size: Number of connections to maintain in the pool (default: 5)
        - max_overflow: Max additional connections beyond pool_size (default: 10)
        - pool_timeout: Seconds to wait for connection from pool (default: 30)
        - pool_recycle: Seconds before recycling connections (default: 3600)
        - pool_pre_ping: Test connections before using them (default: True)
        - echo: Log all SQL statements (default: False)
        """
        if self._engine is not None:
            logger.warning("Database manager already initialized, skipping re-initialization")
            return

        if not connection_string:
            raise ValueError("Connection string is required")

        logger.info("Initializing database connection pool with pool_size=%d, max_overflow=%d", pool_size, max_overflow)

        # Create engine with connection pooling
        self._engine = sa.create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )

        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

        logger.info("Database connection pool initialized successfully")

    def get_engine(self) -> Engine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("DatabaseManager not initialized. Call initialize() first.")
        return self._engine

    def get_session(self) -> Session:
        """Get a new database session."""
        if self._session_factory is None:
            raise RuntimeError("DatabaseManager not initialized. Call initialize() first.")
        return self._session_factory()

    def dispose(self) -> None:
        """Dispose of the database connection pool."""
        if self._engine is not None:
            logger.info("Disposing database connection pool")
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection pool disposed")

    @property
    def is_initialized(self) -> bool:
        """Check if the database manager is initialized."""
        return self._engine is not None


class SuggestionsDBManager:
    """Singleton database connection manager for suggestions database."""

    _instance: SuggestionsDBManager | None = None
    _engine: Engine | None = None
    _session_factory: sessionmaker[Session] | None = None

    def __new__(cls) -> SuggestionsDBManager:
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        connection_string: str,
        pool_size: int = 3,
        max_overflow: int = 5,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ) -> None:
        """
        Initialize the suggestions database connection pool.

        Parameters are similar to DatabaseManager but with smaller defaults
        since suggestions DB typically has lower traffic.
        """
        if self._engine is not None:
            logger.warning("Suggestions DB manager already initialized, skipping re-initialization")
            return

        if not connection_string:
            raise ValueError("Connection string is required")

        logger.info(
            "Initializing suggestions database connection pool with pool_size=%d, max_overflow=%d",
            pool_size,
            max_overflow,
        )

        self._engine = sa.create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )

        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

        logger.info("Suggestions database connection pool initialized successfully")

    def get_engine(self) -> Engine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("SuggestionsDBManager not initialized. Call initialize() first.")
        return self._engine

    def get_session(self) -> Session:
        """Get a new database session."""
        if self._session_factory is None:
            raise RuntimeError("SuggestionsDBManager not initialized. Call initialize() first.")
        return self._session_factory()

    def dispose(self) -> None:
        """Dispose of the database connection pool."""
        if self._engine is not None:
            logger.info("Disposing suggestions database connection pool")
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Suggestions database connection pool disposed")

    @property
    def is_initialized(self) -> bool:
        """Check if the database manager is initialized."""
        return self._engine is not None


# Global singleton instances
db_manager = DatabaseManager()
suggestions_db_manager = SuggestionsDBManager()
