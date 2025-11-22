"""
Redis client for pub/sub and presence management.
"""
import json
import asyncio
import redis.asyncio as redis
from typing import Optional, Callable, Any
from app.core.config import settings


class RedisClient:
    """Redis client wrapper for async operations."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
    
    async def connect(self):
        """Connect to Redis."""
        self.client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        self.pubsub = self.client.pubsub()
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.client:
            await self.client.close()
    
    async def publish(self, channel: str, message: dict):
        """Publish a message to a Redis channel."""
        if not self.client:
            await self.connect()
        await self.client.publish(
            f"{settings.REDIS_PUBSUB_PREFIX}{channel}",
            json.dumps(message)
        )
    
    async def subscribe(self, channel: str, callback: Callable[[dict], Any]):
        """Subscribe to a Redis channel."""
        if not self.pubsub:
            await self.connect()
        await self.pubsub.subscribe(f"{settings.REDIS_PUBSUB_PREFIX}{channel}")
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except (json.JSONDecodeError, KeyError):
                        pass
        except asyncio.CancelledError:
            await self.pubsub.unsubscribe(f"{settings.REDIS_PUBSUB_PREFIX}{channel}")
            raise
    
    async def set_presence(self, user_id: int, status: str, ttl: int = 300):
        """Set user presence with TTL."""
        if not self.client:
            await self.connect()
        key = f"{settings.REDIS_PRESENCE_PREFIX}user:{user_id}"
        await self.client.setex(key, ttl, status)
    
    async def get_presence(self, user_id: int) -> Optional[str]:
        """Get user presence status."""
        if not self.client:
            await self.connect()
        key = f"{settings.REDIS_PRESENCE_PREFIX}user:{user_id}"
        return await self.client.get(key)
    
    async def delete_presence(self, user_id: int):
        """Delete user presence."""
        if not self.client:
            await self.connect()
        key = f"{settings.REDIS_PRESENCE_PREFIX}user:{user_id}"
        await self.client.delete(key)
    
    async def set_typing(self, room_id: int, user_id: int, ttl: int = 5):
        """Set typing indicator with short TTL."""
        if not self.client:
            await self.connect()
        key = f"typing:room:{room_id}:user:{user_id}"
        await self.client.setex(key, ttl, "1")
    
    async def get_typing_users(self, room_id: int) -> list[int]:
        """Get list of users currently typing in a room."""
        if not self.client:
            await self.connect()
        pattern = f"typing:room:{room_id}:user:*"
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        user_ids = [int(key.split(":")[-1]) for key in keys]
        return user_ids


redis_client = RedisClient()

