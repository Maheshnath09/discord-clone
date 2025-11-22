"""
WebSocket connection manager with Redis pub/sub support.
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from app.core.redis_client import redis_client


class ConnectionManager:
    """Manages WebSocket connections and Redis pub/sub."""
    
    def __init__(self):
        # room_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id
        self.user_connections: Dict[WebSocket, int] = {}
        # websocket -> Set[room_id]
        self.websocket_rooms: Dict[WebSocket, Set[int]] = {}
        self._redis_subscription_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize Redis connection and start subscription task."""
        await redis_client.connect()
        # Start background task to listen for Redis pub/sub messages
        self._redis_subscription_task = asyncio.create_task(self._redis_listener())
    
    async def cleanup(self):
        """Cleanup connections and Redis."""
        if self._redis_subscription_task:
            self._redis_subscription_task.cancel()
            try:
                await self._redis_subscription_task
            except asyncio.CancelledError:
                pass
        await redis_client.disconnect()
    
    async def connect(self, websocket: WebSocket, user_id: int, room_id: int):
        """Connect a WebSocket for a user in a room."""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.user_connections[websocket] = user_id
        
        if websocket not in self.websocket_rooms:
            self.websocket_rooms[websocket] = set()
        self.websocket_rooms[websocket].add(room_id)
        
        # Set presence
        await redis_client.set_presence(user_id, "online")
        
        # Broadcast presence update
        await self._broadcast_presence(room_id, user_id, "online")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket."""
        user_id = self.user_connections.get(websocket)
        rooms = self.websocket_rooms.get(websocket, set())
        
        # Remove from all rooms
        for room_id in rooms:
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
        
        # Clean up user tracking
        if websocket in self.user_connections:
            del self.user_connections[websocket]
        if websocket in self.websocket_rooms:
            del self.websocket_rooms[websocket]
        
        # Update presence
        if user_id:
            await redis_client.delete_presence(user_id)
            # Broadcast offline status to all rooms user was in
            for room_id in rooms:
                await self._broadcast_presence(room_id, user_id, "offline")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception:
            # Connection closed, remove it
            await self.disconnect(websocket)
    
    async def broadcast_to_room(self, room_id: int, message: dict, exclude_websocket: Optional[WebSocket] = None):
        """Broadcast a message to all connections in a room."""
        if room_id not in self.active_connections:
            return
        
        # Send to local connections
        disconnected = []
        for connection in self.active_connections[room_id]:
            if connection == exclude_websocket:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)
        
        # Also publish to Redis for other instances
        await redis_client.publish(f"room:{room_id}", message)
    
    async def _broadcast_presence(self, room_id: int, user_id: int, status: str):
        """Broadcast presence update to a room."""
        message = {
            "type": "presence.update",
            "data": {
                "user_id": user_id,
                "status": status,
                "room_id": room_id,
            }
        }
        await self.broadcast_to_room(room_id, message)
    
    async def _redis_listener(self):
        """Background task to listen for Redis pub/sub messages."""
        # Subscribe to a general channel for all room messages
        # In production, you might want to subscribe to specific room channels
        channel = "room:*"
        
        async def handle_message(data: dict):
            """Handle incoming Redis pub/sub message."""
            room_id = data.get("room_id")
            if room_id and room_id in self.active_connections:
                # Broadcast to local connections (exclude sender)
                await self.broadcast_to_room(room_id, data)
        
        try:
            # Subscribe to all room messages
            # Note: This is a simplified approach. In production, you'd want
            # to subscribe to specific room channels dynamically
            await redis_client.subscribe("all_rooms", handle_message)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Log error
            print(f"Redis listener error: {e}")
    
    async def set_typing(self, room_id: int, user_id: int, is_typing: bool):
        """Set typing indicator for a user in a room."""
        await redis_client.set_typing(room_id, user_id, ttl=5 if is_typing else 0)
        
        message = {
            "type": "typing.start" if is_typing else "typing.stop",
            "data": {
                "user_id": user_id,
                "room_id": room_id,
            }
        }
        await self.broadcast_to_room(room_id, message)


# Global instance
websocket_manager = ConnectionManager()

