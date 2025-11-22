"""
User schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    last_seen: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user profile schema."""
    id: int
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True



