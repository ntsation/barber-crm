"""Repository for audit log operations."""
from typing import Optional, List, Any, Dict
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.audit_log import AuditLog as AuditLogModel
from app.schemas.audit_log import AuditLogCreate


class IAuditLogRepository(ABC):
    """Interface for audit log repository."""

    @abstractmethod
    def create(self, audit_log: AuditLogCreate) -> AuditLogModel:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AuditLogModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_entity(
        self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_action(
        self, action: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_all(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditLogModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_entity_history(
        self, entity_type: str, entity_id: int
    ) -> List[AuditLogModel]:
        pass  # pragma: no cover


class AuditLogRepository(IAuditLogRepository):
    """Repository for audit log operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, audit_log: AuditLogCreate) -> AuditLogModel:
        """Create a new audit log entry."""
        db_audit_log = AuditLogModel(**audit_log.model_dump())
        self.db.add(db_audit_log)
        self.db.commit()
        self.db.refresh(db_audit_log)
        return db_audit_log

    def get_by_id(self, id: int) -> Optional[AuditLogModel]:
        """Get audit log by ID."""
        return self.db.query(AuditLogModel).filter(AuditLogModel.id == id).first()

    def get_by_entity(
        self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        """Get audit logs for a specific entity."""
        return (
            self.db.query(AuditLogModel)
            .filter(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id,
            )
            .order_by(desc(AuditLogModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        """Get audit logs for a specific user."""
        return (
            self.db.query(AuditLogModel)
            .filter(AuditLogModel.user_id == user_id)
            .order_by(desc(AuditLogModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_action(
        self, action: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLogModel]:
        """Get audit logs by action type."""
        return (
            self.db.query(AuditLogModel)
            .filter(AuditLogModel.action == action)
            .order_by(desc(AuditLogModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditLogModel]:
        """Get all audit logs with optional filters."""
        query = self.db.query(AuditLogModel)

        if filters:
            if filters.get("entity_type"):
                query = query.filter(AuditLogModel.entity_type == filters["entity_type"])
            if filters.get("entity_id"):
                query = query.filter(AuditLogModel.entity_id == filters["entity_id"])
            if filters.get("action"):
                query = query.filter(AuditLogModel.action == filters["action"])
            if filters.get("user_id"):
                query = query.filter(AuditLogModel.user_id == filters["user_id"])
            if filters.get("start_date"):
                query = query.filter(AuditLogModel.created_at >= filters["start_date"])
            if filters.get("end_date"):
                query = query.filter(AuditLogModel.created_at <= filters["end_date"])

        return (
            query.order_by(desc(AuditLogModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_entity_history(
        self, entity_type: str, entity_id: int
    ) -> List[AuditLogModel]:
        """Get complete history for an entity."""
        return (
            self.db.query(AuditLogModel)
            .filter(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id,
            )
            .order_by(AuditLogModel.created_at)
            .all()
        )

    def get_price_history(
        self, entity_type: str, entity_id: int, price_field: str = "price"
    ) -> List[Dict[str, Any]]:
        """Get price change history for an entity."""
        logs = (
            self.db.query(AuditLogModel)
            .filter(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id,
                AuditLogModel.action == "UPDATE",
            )
            .order_by(AuditLogModel.created_at)
            .all()
        )

        price_history = []
        for log in logs:
            if log.changes and price_field in log.changes:
                price_history.append({
                    "date": log.created_at.isoformat(),
                    "old_price": log.changes[price_field].get("old"),
                    "new_price": log.changes[price_field].get("new"),
                    "changed_by": log.user_email,
                    "user_id": log.user_id,
                })

        return price_history
