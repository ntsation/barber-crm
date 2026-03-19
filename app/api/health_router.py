"""Health check endpoints for Barber CRM API."""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint.
    
    Returns:
        Health status of the application and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "up",
            "database": "unknown",
        }
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "up"
        logger.debug("Health check: Database is healthy")
    except Exception as exc:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = "down"
        logger.error(f"Health check: Database is unhealthy - {str(exc)}")
    
    return health_status


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_check() -> Dict[str, str]:
    """Liveness probe endpoint.
    
    Used by Kubernetes to check if the application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness probe endpoint.
    
    Used by Kubernetes to check if the application is ready to serve requests.
    """
    ready = True
    checks = {
        "database": False,
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as exc:
        ready = False
        logger.error(f"Readiness check failed: Database - {str(exc)}")
    
    status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "ready": ready,
            "checks": checks,
        }
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
def ready_alias() -> Dict[str, str]:
    """Alias for readiness check for compatibility."""
    return {"status": "ready"}
