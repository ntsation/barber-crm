"""Tests for middleware."""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware


def create_test_app_with_logging():
    """Create a test app with logging middleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)
    
    @app.get("/success")
    def success_endpoint():
        return {"status": "ok"}
    
    @app.get("/error")
    def error_endpoint():
        raise ValueError("Test error")
    
    @app.get("/http-error")
    def http_error_endpoint():
        raise HTTPException(status_code=400, detail="HTTP error")
    
    return app


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""

    def test_request_id_in_response(self):
        """Test that request ID is added to response headers."""
        app = create_test_app_with_logging()
        client = TestClient(app)
        
        response = client.get("/success")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_request_id_unique_per_request(self):
        """Test that each request gets a unique ID."""
        app = create_test_app_with_logging()
        client = TestClient(app)
        
        response1 = client.get("/success")
        response2 = client.get("/success")
        
        request_id_1 = response1.headers["X-Request-ID"]
        request_id_2 = response2.headers["X-Request-ID"]
        
        assert request_id_1 != request_id_2

    def test_exception_logging(self, caplog):
        """Test that exceptions are logged properly."""
        import logging
        
        app = create_test_app_with_logging()
        client = TestClient(app)
        
        with caplog.at_level(logging.ERROR):
            # Exception will be raised but caught by the middleware
            with pytest.raises(ValueError):
                client.get("/error")
        
        # Check that error was logged
        assert any("Request failed" in record.message for record in caplog.records)

    def test_http_exception_handling(self, caplog):
        """Test that HTTP exceptions are handled properly."""
        import logging
        
        app = create_test_app_with_logging()
        client = TestClient(app)
        
        with caplog.at_level(logging.WARNING):
            response = client.get("/http-error")
        
        assert response.status_code == 400


def create_test_app_with_security():
    """Create a test app with security headers middleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/")
    def root():
        return {"status": "ok"}
    
    return app


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    def test_security_headers_present(self):
        """Test that security headers are added to responses."""
        app = create_test_app_with_security()
        client = TestClient(app)
        
        response = client.get("/")
        assert response.status_code == 200
        
        # Check security headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
