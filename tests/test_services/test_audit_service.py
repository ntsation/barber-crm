"""Tests for AuditService."""
import pytest
from datetime import datetime

from app.services.audit_service import AuditService
from app.repositories.audit_log_repository import AuditLogRepository


def get_service(db):
    """Helper to create AuditService."""
    return AuditService(AuditLogRepository(db))


class TestLogCreate:
    """Tests for log_create method."""

    def test_log_create(self, db):
        """Test logging a CREATE operation."""
        service = get_service(db)
        
        log = service.log_create(
            entity_type="appointment",
            entity_id=1,
            new_values={"status": "pending", "price": 50.0},
            user_id=1,
            user_email="user@example.com",
            request_info={"request_method": "POST", "request_path": "/api/appointments/"},
        )
        
        assert log.action == "CREATE"
        assert log.entity_type == "appointment"
        assert log.entity_id == 1
        assert log.new_values == {"status": "pending", "price": 50.0}
        assert log.user_id == 1
        assert log.user_email == "user@example.com"

    def test_log_create_without_user(self, db):
        """Test logging CREATE without user info."""
        service = get_service(db)
        
        log = service.log_create(
            entity_type="customer",
            entity_id=2,
            new_values={"name": "John"},
        )
        
        assert log.action == "CREATE"
        assert log.user_id is None


class TestLogUpdate:
    """Tests for log_update method."""

    def test_log_update(self, db):
        """Test logging an UPDATE operation."""
        service = get_service(db)
        
        old_values = {"status": "pending", "price": 50.0}
        new_values = {"status": "confirmed", "price": 55.0}
        
        log = service.log_update(
            entity_type="appointment",
            entity_id=1,
            old_values=old_values,
            new_values=new_values,
            user_id=1,
            description="Updated appointment status",
        )
        
        assert log.action == "UPDATE"
        assert log.old_values == old_values
        assert log.new_values == new_values
        assert log.changes is not None
        assert "status" in log.changes
        assert log.changes["status"]["old"] == "pending"
        assert log.changes["status"]["new"] == "confirmed"

    def test_log_update_calculates_changes(self, db):
        """Test that log_update calculates changes correctly."""
        service = get_service(db)
        
        log = service.log_update(
            entity_type="service",
            entity_id=1,
            old_values={"name": "Corte", "price": 25.0, "active": True},
            new_values={"name": "Corte Premium", "price": 30.0, "active": True},
        )
        
        # Should only include changed fields
        assert "name" in log.changes
        assert "price" in log.changes
        assert "active" not in log.changes  # Not changed


class TestLogDelete:
    """Tests for log_delete method."""

    def test_log_delete(self, db):
        """Test logging a DELETE operation."""
        service = get_service(db)
        
        old_values = {"id": 1, "name": "Test", "status": "active"}
        
        log = service.log_delete(
            entity_type="appointment",
            entity_id=1,
            old_values=old_values,
            user_id=2,
            user_email="admin@example.com",
        )
        
        assert log.action == "DELETE"
        assert log.old_values == old_values
        assert log.new_values is None


class TestLogView:
    """Tests for log_view method."""

    def test_log_view_tracked_entity(self, db):
        """Test logging VIEW for tracked entity."""
        service = get_service(db)
        
        log = service.log_view(
            entity_type="appointment",
            entity_id=1,
            user_id=1,
        )
        
        assert log is not None
        assert log.action == "VIEW"

    def test_log_view_untracked_entity(self, db):
        """Test logging VIEW for untracked entity."""
        service = get_service(db)
        
        # Settings is not in tracked entities
        log = service.log_view(
            entity_type="settings",
            entity_id=1,
        )
        
        assert log is None


class TestGetEntityHistory:
    """Tests for get_entity_history method."""

    def test_get_entity_history(self, db):
        """Test getting entity history."""
        service = get_service(db)
        
        # Create history
        service.log_create(entity_type="service", entity_id=10, new_values={"name": "A"})
        service.log_update(entity_type="service", entity_id=10, old_values={"name": "A"}, new_values={"name": "B"})
        
        history = service.get_entity_history("service", 10)
        
        assert len(history) == 2


class TestGetPriceHistory:
    """Tests for get_price_history method."""

    def test_get_price_history(self, db):
        """Test getting price history."""
        service = get_service(db)
        
        # Create price changes
        service.log_update(
            entity_type="service",
            entity_id=20,
            old_values={"price": 25.0},
            new_values={"price": 30.0},
            user_email="admin@example.com",
        )
        
        history = service.get_price_history("service", 20)
        
        assert len(history) == 1
        assert history[0]["old_price"] == 25.0
        assert history[0]["new_price"] == 30.0


class TestGetUserActivity:
    """Tests for get_user_activity method."""

    def test_get_user_activity(self, db):
        """Test getting user activity."""
        service = get_service(db)
        
        # Create logs for user
        service.log_create(entity_type="appointment", entity_id=1, new_values={}, user_id=5)
        service.log_create(entity_type="appointment", entity_id=2, new_values={}, user_id=5)
        
        activity = service.get_user_activity(5)
        
        assert len(activity) == 2


class TestGetRecentChanges:
    """Tests for get_recent_changes method."""

    def test_get_recent_changes(self, db):
        """Test getting recent changes."""
        service = get_service(db)
        
        # Create various logs
        service.log_create(entity_type="appointment", entity_id=1, new_values={})
        service.log_create(entity_type="service", entity_id=2, new_values={})
        
        # Get all recent
        changes = service.get_recent_changes()
        assert len(changes) == 2
        
        # Filter by entity_type
        changes = service.get_recent_changes(entity_type="appointment")
        assert len(changes) == 1
        
        # Filter by action
        changes = service.get_recent_changes(action="CREATE")
        assert len(changes) == 2


class TestCalculateChanges:
    """Tests for _calculate_changes method."""

    def test_calculate_changes(self, db):
        """Test calculating changes between old and new values."""
        service = get_service(db)
        
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 1, "b": 5, "d": 4}
        
        changes = service._calculate_changes(old, new)
        
        assert "a" not in changes  # Same
        assert "b" in changes  # Changed
        assert changes["b"]["old"] == 2
        assert changes["b"]["new"] == 5
        assert "c" in changes  # Removed
        assert changes["c"]["old"] == 3
        assert changes["c"]["new"] is None
        assert "d" in changes  # Added
        assert changes["d"]["old"] is None
        assert changes["d"]["new"] == 4
