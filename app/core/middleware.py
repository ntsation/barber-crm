"""Middleware for Barber CRM API."""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        
        extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        }
        
        # Add user ID if available (from auth middleware)
        if hasattr(request.state, "user_id"):
            extra["user_id"] = request.state.user_id

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra=extra
        )

        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log response
            extra.update({
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            })
            
            log_message = (
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration_ms}ms"
            )
            
            if response.status_code >= 500:
                logger.error(log_message, extra=extra)
            elif response.status_code >= 400:
                logger.warning(log_message, extra=extra)
            else:
                logger.info(log_message, extra=extra)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            extra.update({
                "duration_ms": duration_ms,
            })
            logger.exception(
                f"Request failed: {request.method} {request.url.path} - {str(exc)}",
                extra=extra
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
