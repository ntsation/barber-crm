"""Tests for audit API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate


def create_test_audit_logs(db):
    """Helper to create test audit logs."""
    repo = AuditLogRepository(db)
    
    logs = []
    logs.append(repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
        user_email="user1@example.com",
        new_values={"status": "pending"},
    )))
    logs.append(repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
        changes={"status": {"old": "pending", "new": "confirmed"}},
    )))
    logs.append(repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="service",
        entity_id=2,
        user_id=2,
        user_email="user2@example.com",
        new_values={"name": "Haircut"},
    )))
    return logs


class TestGetAuditLogs:
    """Tests for GET /api/audit/ endpoint."""

    def test_get_audit_logs(self, client, db):
        """Test getting all audit logs."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_audit_logs_with_entity_filter(self, client, db):
        """Test getting audit logs filtered by entity_type."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/?entity_type=appointment")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for log in data:
            assert log["entity_type"] == "appointment"

    def test_get_audit_logs_with_action_filter(self, client, db):
        """Test getting audit logs filtered by action."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/?action=CREATE")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for log in data:
            assert log["action"] == "CREATE"

    def test_get_audit_logs_with_pagination(self, client, db):
        """Test getting audit logs with pagination."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/?skip=1&limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestGetEntityAuditHistory:
    """Tests for entity audit history endpoint."""

    def test_get_entity_history(self, client, db):
        """Test getting audit history for specific entity."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/entity/appointment/1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for log in data:
            assert log["entity_type"] == "appointment"
            assert log["entity_id"] == 1

    def test_get_entity_history_response(self, client, db):
        """Test getting entity history response with summary."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/entity/appointment/1/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["entity_type"] == "appointment"
        assert data["entity_id"] == 1
        assert "history" in data
        assert "total_changes" in data
        assert data["total_changes"] == 2


class TestGetPriceHistory:
    """Tests for price history endpoint."""

    def test_get_price_history(self, client, db):
        """Test getting price history for an entity."""
        repo = AuditLogRepository(db)
        repo.create(AuditLogCreate(
            action="UPDATE",
            entity_type="service",
            entity_id=100,
            changes={"price": {"old": 25.0, "new": 30.0}},
            user_email="admin@example.com",
        ))
        
        response = client.get("/api/audit/entity/service/100/price-history")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["old_price"] == 25.0
        assert data[0]["new_price"] == 30.0
        assert data[0]["changed_by"] == "admin@example.com"

    def test_get_price_history_with_field(self, client, db):
        """Test getting price history with custom price field."""
        repo = AuditLogRepository(db)
        repo.create(AuditLogCreate(
            action="UPDATE",
            entity_type="product",
            entity_id=200,
            changes={"cost": {"old": 10.0, "new": 15.0}},
        ))
        
        response = client.get("/api/audit/entity/product/200/price-history?price_field=cost")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestGetUserAuditLogs:
    """Tests for user audit logs endpoint."""

    def test_get_user_audit_logs(self, client, db):
        """Test getting audit logs for specific user."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/user/1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for log in data:
            assert log["user_id"] == 1

    def test_get_user_audit_logs_with_pagination(self, client, db):
        """Test getting user audit logs with pagination."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/user/1?skip=0&limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestGetRecentChanges:
    """Tests for recent changes endpoint."""

    def test_get_recent_changes(self, client, db):
        """Test getting recent changes."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/recent/changes")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_recent_changes_with_filters(self, client, db):
        """Test getting recent changes with filters."""
        create_test_audit_logs(db)
        
        response = client.get("/api/audit/recent/changes?entity_type=appointment&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["entity_type"] == "appointment"
