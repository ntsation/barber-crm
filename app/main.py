"""Main application module for Barber CRM API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.api import api_router
from app.api.health_router import router as health_router
from app.api.audit_router import router as audit_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware
from app.core.audit_middleware import AuditMiddleware

# Setup logging
setup_logging(level="INFO", format_type="structured")

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing barbershops, barbers, customers, and appointments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(audit_router, prefix="/api/audit", tags=["audit"])
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }
