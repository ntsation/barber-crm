"""Schemas for audit log."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class AuditLogBase(BaseModel):
    """Base schema for audit log."""
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log."""
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_ip: Optional[str] = None
    request_user_agent: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None


class AuditLogUpdate(BaseModel):
    """Schema for updating audit log - not used as logs are immutable."""
    pass


class AuditLog(AuditLogBase):
    """Schema for audit log response."""
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_ip: Optional[str] = None
    request_user_agent: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: Optional[str] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class EntityHistoryResponse(BaseModel):
    """Schema for entity history response."""
    entity_type: str
    entity_id: int
    history: list[AuditLog]
    total_changes: int
