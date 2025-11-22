"""
WebSocket endpoints for real-time communication.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import json

from app.core.security import decode_token
from app.core.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember
from app.websockets.manager import websocket_manager

router = APIRouter()


@router.websocket("/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: Optional[str] = Query(None),
):
    """WebSocket endpoint for real-time messaging in a room."""
    # Authenticate user
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    payload = decode_token(token)
    if payload is None:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id_value = payload.get("sub")
    if user_id_value is None:
        await websocket.close(code=1008, reason="Invalid token")
        return
    try:
        user_id = int(user_id_value)
    except (TypeError, ValueError):
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Verify room access
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        room = await db.get(Room, room_id)
        if not room:
            await websocket.close(code=1008, reason="Room not found")
            return
        
        # Check if user is a member (for private rooms)
        if not room.is_public:
            from sqlalchemy import select
            result = await db.execute(
                select(RoomMember).where(
                    RoomMember.room_id == room_id,
                    RoomMember.user_id == user_id,
                )
            )
            if not result.scalar_one_or_none():
                await websocket.close(code=1008, reason="Access denied")
                return
    
    # Connect to room
    await websocket_manager.connect(websocket, user_id, room_id)
    
    try:
        # Send initial connection confirmation
        await websocket_manager.send_personal_message(
            {
                "type": "connection.established",
                "data": {"room_id": room_id, "user_id": user_id},
            },
            websocket,
        )
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                event_type = message_data.get("type")
                
                if event_type == "message.create":
                    # Handle message creation via WebSocket
                    # This would typically go through the REST API, but we can handle it here too
                    content = message_data.get("data", {}).get("content")
                    if content:
                        # Broadcast to room (actual saving should go through REST API)
                        await websocket_manager.broadcast_to_room(
                            room_id,
                            {
                                "type": "message.create",
                                "data": {
                                    "room_id": room_id,
                                    "author_id": user_id,
                                    "content": content,
                                    "timestamp": message_data.get("data", {}).get("timestamp"),
                                },
                            },
                            exclude_websocket=websocket,
                        )
                
                elif event_type == "typing.start":
                    await websocket_manager.set_typing(room_id, user_id, True)
                
                elif event_type == "typing.stop":
                    await websocket_manager.set_typing(room_id, user_id, False)
                
                elif event_type == "presence.update":
                    status = message_data.get("data", {}).get("status", "online")
                    await websocket_manager._broadcast_presence(room_id, user_id, status)
            
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(
                    {"type": "error", "data": {"message": "Invalid JSON"}},
                    websocket,
                )
    
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        await websocket_manager.disconnect(websocket)
        raise

