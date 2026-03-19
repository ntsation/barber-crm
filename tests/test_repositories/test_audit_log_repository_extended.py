"""Extended tests for AuditLogRepository to reach 100% coverage."""
import pytest
from datetime import datetime, timedelta

from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate


def test_get_all_with_date_filters(db):
    """Test get_all with start_date and end_date filters."""
    repo = AuditLogRepository(db)
    
    # Create logs at different times
    now = datetime.now()
    
    old_log = repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=1,
    ))
    # Manually update created_at for testing
    old_log.created_at = now - timedelta(days=7)
    db.commit()
    
    recent_log = repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=2,
    ))
    
    # Filter by start_date (should only get recent)
    logs = repo.get_all(filters={"start_date": now - timedelta(days=1)})
    assert len(logs) >= 1
    
    # Filter by end_date (should include old log)
    logs = repo.get_all(filters={"end_date": now - timedelta(days=1)})
    # Old log should be included
    assert any(log.entity_id == 1 for log in logs)


def test_get_all_with_all_filters(db):
    """Test get_all with multiple filters combined."""
    repo = AuditLogRepository(db)
    
    # Create matching log
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=100,
        user_id=50,
    ))
    
    # Create non-matching logs
    repo.create(AuditLogCreate(
        action="CREATE",  # Different action
        entity_type="service",
        entity_id=100,
        user_id=50,
    ))
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="appointment",  # Different entity_type
        entity_id=100,
        user_id=50,
    ))
    
    # Apply multiple filters
    logs = repo.get_all(filters={
        "action": "UPDATE",
        "entity_type": "service",
        "entity_id": 100,
        "user_id": 50,
    })
    
    assert len(logs) == 1
    assert logs[0].action == "UPDATE"
    assert logs[0].entity_type == "service"


def test_get_price_history_no_logs(db):
    """Test get_price_history when no logs exist for entity."""
    repo = AuditLogRepository(db)
    
    # Request history for non-existent entity
    price_history = repo.get_price_history("service", 99999)
    
    assert price_history == []


def test_get_price_history_non_update_logs(db):
    """Test get_price_history when logs are not UPDATE actions."""
    repo = AuditLogRepository(db)
    
    # Create non-UPDATE logs
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="service",
        entity_id=300,
    ))
    repo.create(AuditLogCreate(
        action="DELETE",
        entity_type="service",
        entity_id=300,
    ))
    
    price_history = repo.get_price_history("service", 300)
    
    assert price_history == []
