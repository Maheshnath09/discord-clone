"""
Message schemas.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """Message creation schema."""
    content: Optional[str] = None
    content_type: str = "text"
    attachment_ids: Optional[List[int]] = None


class MessageUpdate(BaseModel):
    """Message update schema."""
    content: str


class MessageReactionResponse(BaseModel):
    """Message reaction response schema."""
    id: int
    message_id: int
    user_id: int
    emoji: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Message response schema."""
    id: int
    room_id: int
    author_id: int
    content: Optional[str]
    content_type: str
    attachments_json: Optional[str]
    edited_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: datetime
    author: Optional[dict] = None  # Will be populated with user data
    reactions: Optional[List[MessageReactionResponse]] = []
    
    class Config:
        from_attributes = True



