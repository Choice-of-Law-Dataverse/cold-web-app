"""Database connection manager with connection pooling best practices."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class _PooledDBManager:
    """Base singleton database connection manager with proper pooling configuration."""

    _instance: ClassVar[_PooledDBManager | None] = None
    _engine: Engine | None = None
    _session_factory: sessionmaker[Session] | None = None
    _label: str = "database"
    _default_pool_size: int = 5
    _default_max_overflow: int = 10

    def __new__(cls) -> _PooledDBManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        connection_string: str,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ) -> None:
        if self._engine is not None:
            logger.warning("%s manager already initialized, skipping re-initialization", self._label)
            return

        if not connection_string:
            raise ValueError("Connection string is required")

        effective_pool_size = pool_size if pool_size is not None else self._default_pool_size
        effective_max_overflow = max_overflow if max_overflow is not None else self._default_max_overflow

        logger.info(
            "Initializing %s connection pool with pool_size=%d, max_overflow=%d",
            self._label,
            effective_pool_size,
            effective_max_overflow,
        )

        self._engine = sa.create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=effective_pool_size,
            max_overflow=effective_max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )

        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        logger.info("%s connection pool initialized successfully", self._label)

    def get_engine(self) -> Engine:
        if self._engine is None:
            raise RuntimeError(f"{self._label} manager not initialized. Call initialize() first.")
        return self._engine

    def get_session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError(f"{self._label} manager not initialized. Call initialize() first.")
        return self._session_factory()

    def dispose(self) -> None:
        if self._engine is not None:
            logger.info("Disposing %s connection pool", self._label)
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("%s connection pool disposed", self._label)

    @property
    def is_initialized(self) -> bool:
        return self._engine is not None


class DatabaseManager(_PooledDBManager):
    _instance: ClassVar[DatabaseManager | None] = None  # type: ignore[assignment]
    _label = "database"
    _default_pool_size = 5
    _default_max_overflow = 10


class SuggestionsDBManager(_PooledDBManager):
    _instance: ClassVar[SuggestionsDBManager | None] = None  # type: ignore[assignment]
    _label = "suggestions"
    _default_pool_size = 3
    _default_max_overflow = 5


db_manager = DatabaseManager()
suggestions_db_manager = SuggestionsDBManager()
