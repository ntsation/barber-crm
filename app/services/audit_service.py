"""Audit service for logging all operations."""
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories.audit_log_repository import IAuditLogRepository
from app.schemas.audit_log import AuditLogCreate, AuditLogFilter
from app.models.audit_log import AuditLog as AuditLogModel


class AuditService:
    """Service for handling audit logging operations."""

    def __init__(self, audit_repo: IAuditLogRepository):
        self.audit_repo = audit_repo

    def log_create(
        self,
        entity_type: str,
        entity_id: int,
        new_values: Dict[str, Any],
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> AuditLogModel:
        """Log a CREATE operation."""
        audit_data = AuditLogCreate(
            action="CREATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            new_values=new_values,
            description=description or f"Created {entity_type} with id {entity_id}",
            **(request_info or {}),
        )
        return self.audit_repo.create(audit_data)

    def log_update(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> AuditLogModel:
        """Log an UPDATE operation with changes."""
        changes = self._calculate_changes(old_values, new_values)
        
        audit_data = AuditLogCreate(
            action="UPDATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description or f"Updated {entity_type} with id {entity_id}",
            **(request_info or {}),
        )
        return self.audit_repo.create(audit_data)

    def log_delete(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> AuditLogModel:
        """Log a DELETE operation."""
        audit_data = AuditLogCreate(
            action="DELETE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            description=description or f"Deleted {entity_type} with id {entity_id}",
            **(request_info or {}),
        )
        return self.audit_repo.create(audit_data)

    def log_view(
        self,
        entity_type: str,
        entity_id: int,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None,
    ) -> Optional[AuditLogModel]:
        """Log a VIEW operation (optional, use with caution to avoid spam)."""
        # Only log views for sensitive entities
        if entity_type not in ["appointment", "customer", "barber"]:
            return None
            
        audit_data = AuditLogCreate(
            action="VIEW",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            description=f"Viewed {entity_type} with id {entity_id}",
            **(request_info or {}),
        )
        return self.audit_repo.create(audit_data)

    def get_entity_history(
        self, entity_type: str, entity_id: int
    ) -> List[AuditLogModel]:
        """Get complete history for an entity."""
        return self.audit_repo.get_entity_history(entity_type, entity_id)

    def get_price_history(
        self, entity_type: str, entity_id: int, price_field: str = "price"
    ) -> List[Dict[str, Any]]:
        """Get price change history for an entity."""
        return self.audit_repo.get_price_history(entity_type, entity_id, price_field)

    def get_user_activity(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        """Get activity history for a user."""
        return self.audit_repo.get_by_user(user_id, skip, limit)

    def get_recent_changes(
        self,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLogModel]:
        """Get recent changes with optional filters."""
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type
        if action:
            filters["action"] = action
        return self.audit_repo.get_all(skip, limit, filters)

    def _calculate_changes(
        self, old_values: Dict[str, Any], new_values: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate the differences between old and new values."""
        changes = {}
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val,
                }
        
        return changes
