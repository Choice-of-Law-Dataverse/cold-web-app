"""HTTP session manager with connection pooling for API clients."""

from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class HTTPSessionManager:
    """Singleton HTTP session manager with connection pooling."""

    _instance: HTTPSessionManager | None = None
    _session: requests.Session | None = None

    def __new__(cls) -> HTTPSessionManager:
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        timeout: int = 30,
    ) -> None:
        """
        Initialize the HTTP session with connection pooling.

        Parameters:
        - pool_connections: Number of connection pools to cache (default: 10)
        - pool_maxsize: Maximum number of connections to save in the pool (default: 20)
        - max_retries: Maximum number of retries for failed requests (default: 3)
        - backoff_factor: Backoff factor for retries (default: 0.3)
        - timeout: Default timeout for requests in seconds (default: 30)
        """
        if self._session is not None:
            logger.warning("HTTP session manager already initialized, skipping re-initialization")
            return

        logger.info(
            "Initializing HTTP session with pool_connections=%d, pool_maxsize=%d",
            pool_connections,
            pool_maxsize,
        )

        # Create session
        self._session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        # Create HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy,
        )

        # Mount adapter for both http and https
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default timeout
        self._session.timeout = timeout  # type: ignore[attr-defined]

        logger.info("HTTP session initialized successfully")

    def get_session(self) -> requests.Session:
        """Get the HTTP session."""
        if self._session is None:
            # Auto-initialize with default settings if not already initialized
            logger.info("HTTP session not initialized, initializing with defaults")
            self.initialize()
        assert self._session is not None
        return self._session

    def close(self) -> None:
        """Close the HTTP session and release connections."""
        if self._session is not None:
            logger.info("Closing HTTP session")
            self._session.close()
            self._session = None
            logger.info("HTTP session closed")

    @property
    def is_initialized(self) -> bool:
        """Check if the HTTP session manager is initialized."""
        return self._session is not None


# Global singleton instance
http_session_manager = HTTPSessionManager()
