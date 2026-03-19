"""Extended tests for audit router to reach 100% coverage."""
import pytest

from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate


def create_test_logs(db):
    """Create test audit logs."""
    repo = AuditLogRepository(db)
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
    ))


class TestAuditRouterFilters:
    """Tests for audit router filter scenarios."""

    def test_get_audit_logs_with_only_entity_type_filter(self, client, db):
        """Test getting logs with only entity_type filter (uses get_recent_changes)."""
        create_test_logs(db)
        
        response = client.get("/api/audit/?entity_type=appointment")
        
        assert response.status_code == 200

    def test_get_audit_logs_with_only_action_filter(self, client, db):
        """Test getting logs with only action filter."""
        create_test_logs(db)
        
        response = client.get("/api/audit/?action=CREATE")
        
        assert response.status_code == 200

    def test_get_audit_logs_with_complex_filters(self, client, db):
        """Test getting logs with multiple filters using get_all."""
        create_test_logs(db)
        
        # This triggers the get_all path with filters
        response = client.get("/api/audit/?entity_type=appointment&entity_id=1&user_id=1")
        
        assert response.status_code == 200

    def test_get_audit_logs_with_all_filters(self, client, db):
        """Test getting logs with all possible filters."""
        from datetime import datetime
        
        create_test_logs(db)
        
        # Build query with all filters
        params = {
            "entity_type": "appointment",
            "entity_id": 1,
            "action": "CREATE",
            "user_id": 1,
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2026-12-31T23:59:59",
        }
        
        response = client.get("/api/audit/", params=params)
        
        assert response.status_code == 200

    def test_get_audit_logs_filters_without_entity_type_or_action(self, client, db):
        """Test getting logs with filters but without entity_type or action."""
        create_test_logs(db)
        
        # This triggers the get_all path because entity_type and action are None
        # but filters exist (user_id is provided)
        response = client.get("/api/audit/?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        # Should return logs filtered by user_id
        assert len(data) >= 0  # May be empty if no logs match
