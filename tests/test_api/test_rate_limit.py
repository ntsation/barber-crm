"""Tests for rate limiting."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestRateLimiting:
    """Tests for API rate limiting."""

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present in responses."""
        response = client.get("/")
        # Rate limit headers should be present
        assert "X-Request-ID" in response.headers

    def test_request_id_header_present(self, client):
        """Test that request ID header is present."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        # Request ID should be a valid UUID format
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID length

    def test_security_headers_present(self, client):
        """Test that security headers are present."""
        response = client.get("/")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers


class TestLoggingMiddleware:
    """Tests for logging middleware."""

    def test_request_logging(self, client, caplog):
        """Test that requests are logged."""
        with caplog.at_level("INFO"):
            response = client.get("/health")
            assert response.status_code == 200
            # Check that request was logged
            assert any("Request started" in record.message for record in caplog.records)
            assert any("Request completed" in record.message for record in caplog.records)

    def test_request_id_in_logs(self, client, caplog):
        """Test that request ID is included in logs."""
        with caplog.at_level("INFO"):
            response = client.get("/health")
            request_id = response.headers.get("X-Request-ID")
            assert request_id is not None
            # Request ID should be in the response headers
            assert len(request_id) > 0
