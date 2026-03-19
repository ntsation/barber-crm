"""Tests for AuditLogRepository."""
import pytest
from datetime import datetime, timedelta

from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate


def test_create_audit_log(db):
    """Test creating an audit log entry."""
    repo = AuditLogRepository(db)
    
    audit_data = AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
        user_email="test@example.com",
        request_method="POST",
        request_path="/api/appointments/",
        new_values={"status": "pending"},
        description="Created appointment",
    )
    
    log = repo.create(audit_data)
    
    assert log.id is not None
    assert log.action == "CREATE"
    assert log.entity_type == "appointment"
    assert log.entity_id == 1
    assert log.user_id == 1
    assert log.user_email == "test@example.com"
    assert log.description == "Created appointment"


def test_get_by_id(db):
    """Test getting audit log by ID."""
    repo = AuditLogRepository(db)
    
    audit_data = AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=2,
        changes={"price": {"old": 25.0, "new": 30.0}},
    )
    
    created = repo.create(audit_data)
    retrieved = repo.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.action == "UPDATE"


def test_get_by_id_not_found(db):
    """Test getting non-existent audit log."""
    repo = AuditLogRepository(db)
    
    result = repo.get_by_id(99999)
    assert result is None


def test_get_by_entity(db):
    """Test getting audit logs by entity."""
    repo = AuditLogRepository(db)
    
    # Create multiple logs
    for i in range(3):
        audit_data = AuditLogCreate(
            action="UPDATE",
            entity_type="appointment",
            entity_id=100,
            description=f"Update {i}",
        )
        repo.create(audit_data)
    
    # Create log for different entity
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="appointment",
        entity_id=200,
    ))
    
    logs = repo.get_by_entity("appointment", 100)
    
    assert len(logs) == 3
    for log in logs:
        assert log.entity_type == "appointment"
        assert log.entity_id == 100


def test_get_by_user(db):
    """Test getting audit logs by user."""
    repo = AuditLogRepository(db)
    
    # Create logs for user 1
    for i in range(2):
        repo.create(AuditLogCreate(
            action="CREATE",
            entity_type="customer",
            user_id=1,
            user_email="user1@example.com",
        ))
    
    # Create log for user 2
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="customer",
        user_id=2,
    ))
    
    logs = repo.get_by_user(1)
    
    assert len(logs) == 2
    for log in logs:
        assert log.user_id == 1


def test_get_by_action(db):
    """Test getting audit logs by action."""
    repo = AuditLogRepository(db)
    
    # Create CREATE logs
    for i in range(2):
        repo.create(AuditLogCreate(
            action="CREATE",
            entity_type="service",
        ))
    
    # Create UPDATE logs
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
    ))
    
    logs = repo.get_by_action("CREATE")
    
    assert len(logs) == 2
    for log in logs:
        assert log.action == "CREATE"


def test_get_all_with_filters(db):
    """Test getting all audit logs with filters."""
    repo = AuditLogRepository(db)
    
    # Create various logs
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
    ))
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="appointment",
        entity_id=1,
        user_id=1,
    ))
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="service",
        entity_id=2,
        user_id=2,
    ))
    
    # Filter by entity_type
    logs = repo.get_all(filters={"entity_type": "appointment"})
    assert len(logs) == 2
    
    # Filter by action
    logs = repo.get_all(filters={"action": "CREATE"})
    assert len(logs) == 2
    
    # Filter by user_id
    logs = repo.get_all(filters={"user_id": 1})
    assert len(logs) == 2


def test_get_entity_history(db):
    """Test getting complete history for an entity."""
    repo = AuditLogRepository(db)
    
    # Create history for entity
    repo.create(AuditLogCreate(
        action="CREATE",
        entity_type="service",
        entity_id=50,
        created_at=datetime.now() - timedelta(days=2),
    ))
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=50,
        created_at=datetime.now() - timedelta(days=1),
    ))
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=50,
        created_at=datetime.now(),
    ))
    
    history = repo.get_entity_history("service", 50)
    
    assert len(history) == 3
    # Should be ordered by created_at
    assert history[0].action == "CREATE"


def test_get_price_history(db):
    """Test getting price change history."""
    repo = AuditLogRepository(db)
    
    # Create price change logs
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=100,
        changes={
            "price": {"old": 20.0, "new": 25.0},
            "name": {"old": "Corte", "new": "Corte Premium"},
        },
        user_email="admin@example.com",
        user_id=1,
    ))
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=100,
        changes={
            "price": {"old": 25.0, "new": 30.0},
        },
        user_email="manager@example.com",
        user_id=2,
    ))
    
    price_history = repo.get_price_history("service", 100)
    
    assert len(price_history) == 2
    assert price_history[0]["old_price"] == 20.0
    assert price_history[0]["new_price"] == 25.0
    assert price_history[0]["changed_by"] == "admin@example.com"
    assert price_history[1]["old_price"] == 25.0
    assert price_history[1]["new_price"] == 30.0


def test_get_price_history_no_price_changes(db):
    """Test price history when no price changes exist."""
    repo = AuditLogRepository(db)
    
    repo.create(AuditLogCreate(
        action="UPDATE",
        entity_type="service",
        entity_id=200,
        changes={"name": {"old": "Old", "new": "New"}},
    ))
    
    price_history = repo.get_price_history("service", 200)
    
    assert len(price_history) == 0
