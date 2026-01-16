"""
WebSocket connection manager with optional Redis pub/sub support.
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and optional Redis pub/sub."""
    
    def __init__(self):
        # room_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id
        self.user_connections: Dict[WebSocket, int] = {}
        # websocket -> Set[room_id]
        self.websocket_rooms: Dict[WebSocket, Set[int]] = {}
        self._redis_subscription_task: Optional[asyncio.Task] = None
        self._redis_available = False
    
    async def initialize(self):
        """Initialize Redis connection (optional) and start subscription task."""
        try:
            from app.core.redis_client import redis_client
            await redis_client.connect()
            self._redis_available = True
            # Start background task to listen for Redis pub/sub messages
            self._redis_subscription_task = asyncio.create_task(self._redis_listener())
            logger.info("WebSocket manager initialized with Redis support")
        except Exception as e:
            logger.warning(f"Redis connection failed, running without Redis: {e}")
            self._redis_available = False
    
    async def cleanup(self):
        """Cleanup connections and Redis."""
        if self._redis_subscription_task:
            self._redis_subscription_task.cancel()
            try:
                await self._redis_subscription_task
            except asyncio.CancelledError:
                pass
        if self._redis_available:
            try:
                from app.core.redis_client import redis_client
                await redis_client.disconnect()
            except Exception:
                pass
    
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
        
        # Log connection for debugging
        connection_count = len(self.active_connections.get(room_id, set()))
        logger.info(f"WebSocket connected: user={user_id}, room={room_id}, total_connections={connection_count}")
        
        # Set presence (optional - don't fail if Redis unavailable)
        if self._redis_available:
            try:
                from app.core.redis_client import redis_client
                await redis_client.set_presence(user_id, "online")
            except Exception as e:
                logger.warning(f"Failed to set presence: {e}")
        
        # Broadcast presence update
        await self._broadcast_presence(room_id, user_id, "online")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket."""
        user_id = self.user_connections.get(websocket)
        rooms = self.websocket_rooms.get(websocket, set()).copy()  # Copy to avoid modification during iteration
        
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
        
        logger.info(f"WebSocket disconnected: user={user_id}, rooms={list(rooms)}")
        
        # Update presence (optional)
        if user_id and self._redis_available:
            try:
                from app.core.redis_client import redis_client
                await redis_client.delete_presence(user_id)
            except Exception:
                pass
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
        # Use print for immediate visibility (logging might be buffered)
        print(f"[BROADCAST] broadcast_to_room called for room {room_id}, type={message.get('type')}")
        print(f"[BROADCAST] Active rooms: {list(self.active_connections.keys())}")
        
        connections = self.active_connections.get(room_id, set())
        
        if not connections:
            print(f"[BROADCAST] No active connections for room {room_id}")
            logger.debug(f"No active connections for room {room_id}")
            return
        
        print(f"[BROADCAST] Broadcasting to {len(connections)} connections")
        logger.info(f"Broadcasting to room {room_id}: {len(connections)} connections, message_type={message.get('type')}")
        
        # Send to local connections
        disconnected = []
        sent_count = 0
        for connection in connections.copy():  # Copy to avoid modification during iteration
            if connection == exclude_websocket:
                continue
            try:
                await connection.send_json(message)
                sent_count += 1
                print(f"[BROADCAST] Successfully sent to connection {sent_count}")
                logger.debug(f"Sent message to connection in room {room_id}")
            except Exception as e:
                print(f"[BROADCAST] Failed to send to connection: {e}")
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        print(f"[BROADCAST] Complete: sent to {sent_count} connections")
        logger.info(f"Broadcast complete: sent to {sent_count} connections")
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect(ws)
        
        # Also publish to Redis for other instances (optional)
        if self._redis_available:
            try:
                from app.core.redis_client import redis_client
                await redis_client.publish(f"room:{room_id}", message)
            except Exception as e:
                logger.warning(f"Failed to publish to Redis: {e}")
    
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
        if not self._redis_available:
            return
            
        async def handle_message(data: dict):
            """Handle incoming Redis pub/sub message."""
            room_id = data.get("room_id")
            if room_id and room_id in self.active_connections:
                await self.broadcast_to_room(room_id, data)
        
        try:
            from app.core.redis_client import redis_client
            await redis_client.subscribe("all_rooms", handle_message)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
    
    async def set_typing(self, room_id: int, user_id: int, is_typing: bool):
        """Set typing indicator for a user in a room."""
        if self._redis_available:
            try:
                from app.core.redis_client import redis_client
                await redis_client.set_typing(room_id, user_id, ttl=5 if is_typing else 0)
            except Exception:
                pass
        
        message = {
            "type": "typing.start" if is_typing else "typing.stop",
            "data": {
                "user_id": user_id,
                "room_id": room_id,
            }
        }
        await self.broadcast_to_room(room_id, message)
    
    def get_connection_stats(self) -> dict:
        """Get current connection statistics for debugging."""
        return {
            "rooms": {room_id: len(conns) for room_id, conns in self.active_connections.items()},
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "redis_available": self._redis_available,
        }


# Global instance
websocket_manager = ConnectionManager()


