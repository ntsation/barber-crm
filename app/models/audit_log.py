"""Audit log model for tracking all operations."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class AuditLog(Base):
    """Model for storing audit logs of all operations."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    
    # Operation details
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, VIEW
    entity_type = Column(String(50), nullable=False)  # appointment, service, barber, etc
    entity_id = Column(Integer, nullable=True)
    
    # Request details
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_ip = Column(String(50), nullable=True)
    request_user_agent = Column(String(500), nullable=True)
    
    # Data changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)
    
    # Additional context
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="audit_logs")
