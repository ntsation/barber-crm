"""Middleware for capturing audit information from requests."""
from typing import Optional, Dict, Any, Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditContext:
    """Context manager for audit information."""
    
    _current_user_id: Optional[int] = None
    _current_user_email: Optional[str] = None
    
    @classmethod
    def set_current_user(cls, user_id: Optional[int], user_email: Optional[str]):
        """Set current user for audit context."""
        cls._current_user_id = user_id
        cls._current_user_email = user_email
    
    @classmethod
    def get_current_user(cls) -> tuple[Optional[int], Optional[str]]:
        """Get current user from audit context."""
        return cls._current_user_id, cls._current_user_email
    
    @classmethod
    def clear(cls):
        """Clear audit context."""
        cls._current_user_id = None
        cls._current_user_email = None


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for capturing audit information."""

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and capture audit information."""
        # Extract user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        user_email = getattr(request.state, "user_email", None)
        
        # Set audit context
        AuditContext.set_current_user(user_id, user_email)
        
        # Extract request info for potential audit logging
        request_info = {
            "request_method": request.method,
            "request_path": str(request.url.path),
            "request_ip": self._get_client_ip(request),
            "request_user_agent": request.headers.get("user-agent", ""),
        }
        
        # Store request info in state for later use
        request.state.audit_info = request_info
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Clear audit context after request
            AuditContext.clear()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"


def get_request_info(request: Request) -> Dict[str, str]:
    """Get audit request info from request state."""
    return getattr(request.state, "audit_info", {
        "request_method": request.method,
        "request_path": str(request.url.path),
        "request_ip": "unknown",
        "request_user_agent": "",
    })


def get_current_user_info() -> tuple[Optional[int], Optional[str]]:
    """Get current user info from audit context."""
    return AuditContext.get_current_user()
