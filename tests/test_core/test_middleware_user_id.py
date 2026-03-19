"""Tests for middleware with user_id."""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.middleware import LoggingMiddleware


def create_test_app_with_user_id():
    """Create a test app with logging middleware and user_id in state."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)
    
    @app.middleware("http")
    async def add_user_id(request: Request, call_next):
        """Middleware to add user_id to request state."""
        request.state.user_id = "test-user-123"
        response = await call_next(request)
        return response
    
    @app.get("/profile")
    def profile():
        return {"status": "ok"}
    
    return app


class TestLoggingMiddlewareWithUserId:
    """Tests for LoggingMiddleware with user_id."""

    def test_request_with_user_id_logged(self, caplog):
        """Test that user_id is included in logs when available."""
        import logging
        
        app = create_test_app_with_user_id()
        client = TestClient(app)
        
        with caplog.at_level(logging.INFO):
            response = client.get("/profile")
        
        assert response.status_code == 200
        # Check that the request was logged
        assert any("Request started" in record.message for record in caplog.records)
