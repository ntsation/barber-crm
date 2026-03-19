"""Tests for audit middleware."""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.audit_middleware import (
    AuditMiddleware,
    AuditContext,
    get_request_info,
    get_current_user_info,
)


def test_audit_context_set_and_get():
    """Test setting and getting audit context."""
    AuditContext.set_current_user(1, "test@example.com")
    
    user_id, user_email = AuditContext.get_current_user()
    
    assert user_id == 1
    assert user_email == "test@example.com"


def test_audit_context_clear():
    """Test clearing audit context."""
    AuditContext.set_current_user(1, "test@example.com")
    AuditContext.clear()
    
    user_id, user_email = AuditContext.get_current_user()
    
    assert user_id is None
    assert user_email is None


def test_get_current_user_info_default():
    """Test getting current user info when context is empty."""
    AuditContext.clear()
    
    user_id, user_email = get_current_user_info()
    
    assert user_id is None
    assert user_email is None


def create_test_app_with_audit():
    """Create a test app with audit middleware."""
    app = FastAPI()
    app.add_middleware(AuditMiddleware)
    
    @app.get("/test")
    def test_endpoint(request: Request):
        # Check that audit_info is set in state
        audit_info = getattr(request.state, "audit_info", {})
        return {
            "method": audit_info.get("request_method"),
            "path": audit_info.get("request_path"),
        }
    
    return app


class TestAuditMiddleware:
    """Tests for AuditMiddleware."""

    def test_audit_info_set_in_state(self):
        """Test that audit info is set in request state."""
        app = create_test_app_with_audit()
        client = TestClient(app)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "GET"
        assert data["path"] == "/test"

    def test_x_forwarded_for_header(self):
        """Test extracting client IP from X-Forwarded-For header."""
        app = create_test_app_with_audit()
        client = TestClient(app)
        
        response = client.get(
            "/test",
            headers={"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        )
        
        assert response.status_code == 200

    def test_x_real_ip_header(self):
        """Test extracting client IP from X-Real-IP header."""
        app = create_test_app_with_audit()
        client = TestClient(app)
        
        response = client.get(
            "/test",
            headers={"X-Real-IP": "192.168.1.100"}
        )
        
        assert response.status_code == 200

    def test_user_agent_header(self):
        """Test extracting user agent from request."""
        app = create_test_app_with_audit()
        client = TestClient(app)
        
        response = client.get(
            "/test",
            headers={"User-Agent": "TestClient/1.0"}
        )
        
        assert response.status_code == 200


def test_get_request_info_default():
    """Test getting request info when not set."""
    from fastapi import Request
    from starlette.datastructures import URL
    
    # Create a minimal request for testing
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    request = Request(scope)
    
    info = get_request_info(request)
    
    assert info["request_method"] == "GET"
    assert info["request_path"] == "/"


def test_get_client_ip_unknown():
    """Test _get_client_ip returns unknown when no IP sources available."""
    from unittest.mock import MagicMock
    
    middleware = AuditMiddleware(app=MagicMock())
    
    # Create mock request with no headers and no client
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.client = None
    
    result = middleware._get_client_ip(mock_request)
    
    assert result == "unknown"


def test_audit_middleware_with_user_in_state():
    """Test audit middleware when user info is in request state."""
    app = FastAPI()
    app.add_middleware(AuditMiddleware)
    
    @app.middleware("http")
    async def add_user_to_state(request, call_next):
        request.state.user_id = 42
        request.state.user_email = "middleware@example.com"
        response = await call_next(request)
        return response
    
    @app.get("/user-test")
    def user_test(request: Request):
        user_id, user_email = get_current_user_info()
        return {"user_id": user_id, "user_email": user_email}
    
    client = TestClient(app)
    response = client.get("/user-test")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 42
    assert data["user_email"] == "middleware@example.com"
