"""
Room endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember, RoomRole
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomMemberResponse
from app.api.dependencies import get_current_user, get_optional_current_user

router = APIRouter()


@router.get("", response_model=List[RoomResponse])
async def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List/discover rooms with filtering and pagination."""
    query = select(Room).where(Room.is_direct == False)
    
    # Filter by public/private
    if is_public is not None:
        query = query.where(Room.is_public == is_public)
    
    # Search by name
    if search:
        query = query.where(Room.name.ilike(f"%{search}%"))
    
    # If not authenticated, only show public rooms
    if current_user is None:
        query = query.where(Room.is_public == True)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Room.created_at.desc())
    
    result = await db.execute(query)
    rooms = result.scalars().all()
    
    membership_map = {}
    if current_user and rooms:
        room_ids = [room.id for room in rooms]
        member_rows = await db.execute(
            select(RoomMember.room_id, RoomMember.role).where(
                RoomMember.user_id == current_user.id,
                RoomMember.room_id.in_(room_ids),
            )
        )
        membership_map = {row[0]: row[1] for row in member_rows.all()}
    
    # Add member data
    room_list = []
    for room in rooms:
        room_dict = RoomResponse.model_validate(room).model_dump()
        member_count = await db.scalar(
            select(func.count(RoomMember.id)).where(RoomMember.room_id == room.id)
        )
        membership_role = membership_map.get(room.id)
        is_member = membership_role is not None
        room_dict["member_count"] = member_count
        room_dict["is_member"] = is_member
        room_dict["membership_role"] = membership_role.value if membership_role else None
        room_dict["can_join"] = room.is_public and not is_member
        room_list.append(RoomResponse(**room_dict))
    
    return room_list


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new room."""
    # Check if room name already exists
    result = await db.execute(
        select(Room).where(Room.name == room_data.name, Room.is_direct == False)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room name already exists",
        )
    
    # Create room
    room = Room(
        name=room_data.name,
        description=room_data.description,
        is_public=room_data.is_public,
        owner_id=current_user.id,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    
    # Add creator as owner
    member = RoomMember(
        user_id=current_user.id,
        room_id=room.id,
        role=RoomRole.OWNER,
    )
    db.add(member)
    await db.commit()
    
    return room


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get room details."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    
    # Check access
    if not room.is_public and current_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Room is private",
        )
    
    if not room.is_public:
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
    
    member_count = await db.scalar(
        select(func.count(RoomMember.id)).where(RoomMember.room_id == room_id)
    )
    
    room_dict = RoomResponse.model_validate(room).model_dump()
    room_dict["member_count"] = member_count
    return RoomResponse(**room_dict)


@router.post("/{room_id}/join", response_model=RoomMemberResponse)
async def join_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a room."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    
    # Check if already a member
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == current_user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this room",
        )
    
    # Check if room is public or user has permission
    if not room.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Room is private. You need an invite to join.",
        )
    
    # Add member
    member = RoomMember(
        user_id=current_user.id,
        room_id=room_id,
        role=RoomRole.MEMBER,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return member


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Leave a room."""
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == current_user.id,
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this room",
        )
    
    # Don't allow owner to leave (they should transfer ownership first)
    if member.role == RoomRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room owner cannot leave. Transfer ownership first.",
        )
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Left room successfully"}


@router.get("/{room_id}/members", response_model=List[RoomMemberResponse])
async def get_room_members(
    room_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get room members."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    
    # Check access
    if not room.is_public and (current_user is None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Room is private",
        )
    
    result = await db.execute(
        select(RoomMember).where(RoomMember.room_id == room_id).order_by(RoomMember.joined_at)
    )
    members = result.scalars().all()
    
    # Populate user data
    member_list = []
    for member in members:
        user = await db.get(User, member.user_id)
        member_dict = RoomMemberResponse.model_validate(member).model_dump()
        member_dict["user"] = {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
        }
        member_list.append(RoomMemberResponse(**member_dict))
    
    return member_list



