"""
Room schemas.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.room import RoomRole


class RoomCreate(BaseModel):
    """Room creation schema."""
    name: str
    description: Optional[str] = None
    is_public: bool = True


class RoomUpdate(BaseModel):
    """Room update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class RoomResponse(BaseModel):
    """Room response schema."""
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    is_direct: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    member_count: Optional[int] = None
    is_member: bool = False
    membership_role: Optional[str] = None
    can_join: bool = False
    
    class Config:
        from_attributes = True


class RoomMemberResponse(BaseModel):
    """Room member response schema."""
    id: int
    user_id: int
    room_id: int
    role: RoomRole
    joined_at: datetime
    user: Optional[dict] = None  # Will be populated with user data
    
    class Config:
        from_attributes = True



