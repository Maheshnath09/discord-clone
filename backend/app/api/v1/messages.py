"""
Message endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
import json

from app.core.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember
from app.models.message import Message, MessageReaction
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse, MessageReactionResponse
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    room_id: int,
    cursor: Optional[int] = Query(None, description="Message ID to paginate from"),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages for a room with cursor-based pagination."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    
    # Check access
    if not room.is_public:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        # Check if user is a member
        result = await db.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == current_user.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this room",
            )
    
    # Build query
    query = select(Message).where(
        Message.room_id == room_id,
        Message.deleted_at.is_(None),
    )
    
    # Cursor-based pagination
    if cursor:
        query = query.where(Message.id < cursor)
    
    query = query.order_by(desc(Message.created_at)).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Populate author and reactions
    message_list = []
    for msg in messages:
        author = await db.get(User, msg.author_id)
        reactions_result = await db.execute(
            select(MessageReaction).where(MessageReaction.message_id == msg.id)
        )
        reactions = reactions_result.scalars().all()
        
        msg_dict = MessageResponse.model_validate(msg).model_dump()
        msg_dict["author"] = {
            "id": author.id,
            "username": author.username,
            "display_name": author.display_name,
            "avatar_url": author.avatar_url,
        }
        msg_dict["reactions"] = [MessageReactionResponse.model_validate(r).model_dump() for r in reactions]
        message_list.append(MessageResponse(**msg_dict))
    
    return message_list


@router.post("/{room_id}/messages", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def create_message(
    room_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new message in a room."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    
    # Check if user is a member
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this room",
        )
    
    # Validate content or attachments
    if not message_data.content and not message_data.attachment_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message must have content or attachments",
        )
    
    # Create message
    attachments_json = None
    if message_data.attachment_ids:
        attachments_json = json.dumps(message_data.attachment_ids)
    
    message = Message(
        room_id=room_id,
        author_id=current_user.id,
        content=message_data.content,
        content_type=message_data.content_type,
        attachments_json=attachments_json,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Populate author
    msg_dict = MessageResponse.model_validate(message).model_dump()
    msg_dict["author"] = {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
    }
    msg_dict["reactions"] = []
    
    return MessageResponse(**msg_dict)


@router.patch("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a message (only by author within time limit)."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check ownership
    if message.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own messages",
        )
    
    # Check if message was deleted
    if message.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit deleted message",
        )
    
    # Update message
    message.content = message_data.content
    message.edited_at = datetime.utcnow()
    await db.commit()
    await db.refresh(message)
    
    # Populate author
    author = await db.get(User, message.author_id)
    msg_dict = MessageResponse.model_validate(message).model_dump()
    msg_dict["author"] = {
        "id": author.id,
        "username": author.username,
        "display_name": author.display_name,
        "avatar_url": author.avatar_url,
    }
    
    return MessageResponse(**msg_dict)


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a message (soft delete)."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check ownership or admin role
    is_owner = message.author_id == current_user.id
    
    # Check if user is room admin/owner
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == message.room_id,
            RoomMember.user_id == current_user.id,
        )
    )
    member = result.scalar_one_or_none()
    is_admin = member and member.role in ["admin", "owner"]
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this message",
        )
    
    # Soft delete
    message.deleted_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Message deleted successfully"}


@router.post("/messages/{message_id}/reactions")
async def add_reaction(
    message_id: int,
    emoji: str = Query(..., description="Emoji to react with"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a reaction to a message."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check if reaction already exists
    result = await db.execute(
        select(MessageReaction).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == current_user.id,
            MessageReaction.emoji == emoji,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reaction already exists",
        )
    
    # Create reaction
    reaction = MessageReaction(
        message_id=message_id,
        user_id=current_user.id,
        emoji=emoji,
    )
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    
    return MessageReactionResponse.model_validate(reaction)


@router.delete("/messages/{message_id}/reactions/{reaction_id}")
async def remove_reaction(
    message_id: int,
    reaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a reaction from a message."""
    reaction = await db.get(MessageReaction, reaction_id)
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found",
        )
    
    # Check ownership
    if reaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove your own reactions",
        )
    
    # Check message match
    if reaction.message_id != message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reaction does not belong to this message",
        )
    
    await db.delete(reaction)
    await db.commit()
    
    return {"message": "Reaction removed successfully"}

