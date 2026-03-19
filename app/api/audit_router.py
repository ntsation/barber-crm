"""Audit log endpoints for Barber CRM API."""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit_log import AuditLog, AuditLogFilter, EntityHistoryResponse
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_service import AuditService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_audit_service(db: Session = Depends(get_db)):
    """Factory function to create AuditService."""
    return AuditService(AuditLogRepository(db))


@router.get("/", response_model=List[AuditLog])
def get_audit_logs(
    request: Request,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, UPDATE, DELETE)"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get audit logs with optional filters."""
    filters = {}
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
    if action:
        filters["action"] = action
    if user_id:
        filters["user_id"] = user_id
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date

    logs = audit_service.get_recent_changes(
        entity_type=entity_type,
        action=action,
        skip=skip,
        limit=limit,
    )
    
    # If filters other than entity_type/action, use get_all
    if filters and not (entity_type or action):
        logs = audit_service.audit_repo.get_all(skip, limit, filters)
    
    return logs


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLog])
def get_entity_audit_history(
    request: Request,
    entity_type: str,
    entity_id: int,
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get complete audit history for a specific entity."""
    logger.info(f"Getting audit history for {entity_type} {entity_id}")
    return audit_service.get_entity_history(entity_type, entity_id)


@router.get("/entity/{entity_type}/{entity_id}/history", response_model=EntityHistoryResponse)
def get_entity_history_response(
    request: Request,
    entity_type: str,
    entity_id: int,
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get entity history with summary."""
    history = audit_service.get_entity_history(entity_type, entity_id)
    return EntityHistoryResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        history=history,
        total_changes=len(history),
    )


@router.get("/entity/{entity_type}/{entity_id}/price-history")
def get_price_history(
    request: Request,
    entity_type: str,
    entity_id: int,
    price_field: str = Query("price", description="Field name for price"),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get price change history for an entity."""
    return audit_service.get_price_history(entity_type, entity_id, price_field)


@router.get("/user/{user_id}", response_model=List[AuditLog])
def get_user_audit_logs(
    request: Request,
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get audit logs for a specific user."""
    return audit_service.get_user_activity(user_id, skip, limit)


@router.get("/recent/changes", response_model=List[AuditLog])
def get_recent_changes(
    request: Request,
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get recent changes."""
    return audit_service.get_recent_changes(
        entity_type=entity_type,
        action=action,
        limit=limit,
    )
