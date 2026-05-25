"""Unit tests for database connection pool configuration (PERF-03).

Verifies pool_size=5, max_overflow=5, pool_recycle=1800 as specified
in REQUIREMENTS.md PERF-03.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text


class TestPoolConfiguration:
    """Verify create_engine receives correct pool parameters."""

    def test_pool_size(self, test_engine):
        """pool_size should be 5."""
        pool = test_engine.pool
        # QueuePool exposes pool_size via the _pool maxsize
        actual_size = pool._pool.maxsize
        assert actual_size == 5, (
            f"pool_size should be 5, got {actual_size}"
        )

    def test_max_overflow(self, test_engine):
        """max_overflow should be 5."""
        pool = test_engine.pool
        # QueuePool stores max_overflow configuration
        actual_overflow = pool._max_overflow
        assert actual_overflow == 5, (
            f"max_overflow should be 5, got {actual_overflow}"
        )

    def test_pool_recycle(self, test_engine):
        """pool_recycle should be 1800 (30 minutes)."""
        # The pool_recycle is stored on the dialect or the creator
        # Access via engine's recreation function
        recycle = test_engine.pool._recycle
        assert recycle == 1800, (
            f"pool_recycle should be 1800, got {recycle}"
        )


def test_engine_creates_connection(test_engine):
    """Engine can execute a simple query, confirming connectivity."""
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS one"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1, f"Expected 1, got {row[0]}"
