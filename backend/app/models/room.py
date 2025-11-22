"""
Room and membership models.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class RoomRole(str, enum.Enum):
    """Room member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Room(Base):
    """Room (channel/server) model."""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True, index=True)
    is_direct = Column(Boolean, default=False, index=True)  # For 1:1 chats
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    room_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_rooms", foreign_keys=[owner_id])
    members = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class RoomMember(Base):
    """Room membership model."""
    __tablename__ = "room_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    role = Column(SQLEnum(RoomRole), default=RoomRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    muted_until = Column(DateTime(timezone=True), nullable=True)
    banned_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="room_memberships")
    room = relationship("Room", back_populates="members")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

