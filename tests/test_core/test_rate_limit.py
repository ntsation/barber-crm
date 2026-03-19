"""Tests for rate limiting configuration."""
import pytest

from app.core.rate_limit import (
    get_limiter,
    DEFAULT_RATE_LIMIT,
    STRICT_RATE_LIMIT,
    GENEROUS_RATE_LIMIT,
    CREATE_RATE_LIMIT,
    UPDATE_RATE_LIMIT,
    DELETE_RATE_LIMIT,
    LIST_RATE_LIMIT,
)


class TestRateLimitConstants:
    """Tests for rate limit constants."""

    def test_default_rate_limit(self):
        """Test default rate limit constant."""
        assert DEFAULT_RATE_LIMIT == "100/minute"

    def test_strict_rate_limit(self):
        """Test strict rate limit constant."""
        assert STRICT_RATE_LIMIT == "10/minute"

    def test_generous_rate_limit(self):
        """Test generous rate limit constant."""
        assert GENEROUS_RATE_LIMIT == "1000/minute"

    def test_create_rate_limit(self):
        """Test create rate limit constant."""
        assert CREATE_RATE_LIMIT == "30/minute"

    def test_update_rate_limit(self):
        """Test update rate limit constant."""
        assert UPDATE_RATE_LIMIT == "60/minute"

    def test_delete_rate_limit(self):
        """Test delete rate limit constant."""
        assert DELETE_RATE_LIMIT == "20/minute"

    def test_list_rate_limit(self):
        """Test list rate limit constant."""
        assert LIST_RATE_LIMIT == "100/minute"


class TestGetLimiter:
    """Tests for get_limiter function."""

    def test_get_limiter_returns_limiter(self):
        """Test that get_limiter returns a Limiter instance."""
        from slowapi import Limiter
        limiter = get_limiter()
        assert isinstance(limiter, Limiter)

    def test_get_limiter_uses_remote_address(self):
        """Test that get_limiter uses remote address as key."""
        from slowapi.util import get_remote_address
        limiter = get_limiter()
        # The limiter should be configured with get_remote_address
        assert limiter._key_func == get_remote_address
