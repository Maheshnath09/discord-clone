"""
Audit log model for moderation and tracking.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """Audit log for moderation actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "kick", "ban", "delete_message"
    target_type = Column(String(50), nullable=False)  # "user", "message", "room"
    target_id = Column(Integer, nullable=False, index=True)
    log_metadata = Column(Text, nullable=True)  # JSON string for additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    actor = relationship("User")

