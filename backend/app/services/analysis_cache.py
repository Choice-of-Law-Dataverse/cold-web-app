"""
Simple in-memory cache for case analysis documents.
Uses correlation IDs to link analysis steps.

Note: This is an in-memory cache that will lose data on application restart
and does not scale across multiple instances. For production use with multiple
instances, consider implementing a persistent cache using Redis or similar.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any


class AnalysisCache:
    """In-memory cache for case analysis data with TTL."""

    def __init__(self, ttl_hours: int = 24):
        self._cache: dict[str, dict[str, Any]] = {}
        self._ttl = timedelta(hours=ttl_hours)

    def create_entry(self, text: str, jurisdiction: dict[str, Any]) -> str:
        """Create a new cache entry and return correlation ID."""
        correlation_id = str(uuid.uuid4())
        self._cache[correlation_id] = {
            "text": text,
            "jurisdiction": jurisdiction,
            "created_at": datetime.now(),
            "analysis_results": {},
        }
        return correlation_id

    def get_text(self, correlation_id: str) -> str | None:
        """Get cached text by correlation ID."""
        entry = self._cache.get(correlation_id)
        if entry and self._is_valid(entry):
            return entry["text"]
        return None

    def get_entry(self, correlation_id: str) -> dict[str, Any] | None:
        """Get full cache entry by correlation ID."""
        entry = self._cache.get(correlation_id)
        if entry and self._is_valid(entry):
            return entry
        return None

    def update_results(self, correlation_id: str, step_name: str, result: Any) -> None:
        """Update analysis results for a specific step."""
        entry = self._cache.get(correlation_id)
        if entry and self._is_valid(entry):
            entry["analysis_results"][step_name] = result

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_ids = [
            correlation_id
            for correlation_id, entry in self._cache.items()
            if now - entry["created_at"] > self._ttl
        ]
        for correlation_id in expired_ids:
            del self._cache[correlation_id]

    def _is_valid(self, entry: dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        return datetime.now() - entry["created_at"] <= self._ttl


analysis_cache = AnalysisCache()
