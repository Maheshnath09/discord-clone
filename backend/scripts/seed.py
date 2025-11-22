"""
Seed script to create demo users, rooms, and messages.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from datetime import datetime, timedelta
import random

from app.core.database import Base, AsyncSessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.room import Room, RoomMember, RoomRole
from app.models.message import Message


async def seed_database():
    """Seed the database with demo data."""
    # Create tables
    engine = create_async_engine(settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        # Create demo users
        users = []
        for i in range(5):
            username = f"user{i+1}"
            email = f"{username}@example.com"
            
            # Check if user exists
            result = await db.execute(select(User).where(User.username == username))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                users.append(existing_user)
                continue
            
            user = User(
                username=username,
                email=email,
                password_hash=get_password_hash("password123"),
                display_name=f"User {i+1}",
                bio=f"This is the bio for {username}",
            )
            db.add(user)
            users.append(user)
        
        await db.commit()
        
        # Refresh users to get IDs
        for user in users:
            await db.refresh(user)
        
        # Create demo rooms
        rooms = []
        room_names = [
            "General",
            "Random",
            "Development",
            "Music",
            "Gaming",
        ]
        
        for i, name in enumerate(room_names):
            # Check if room exists
            result = await db.execute(select(Room).where(Room.name == name))
            existing_room = result.scalar_one_or_none()
            
            if existing_room:
                rooms.append(existing_room)
                continue
            
            room = Room(
                name=name,
                description=f"This is the {name} room",
                is_public=True,
                owner_id=users[0].id,
            )
            db.add(room)
            rooms.append(room)
        
        await db.commit()
        
        # Refresh rooms to get IDs
        for room in rooms:
            await db.refresh(room)
        
        # Add users to rooms
        for room in rooms:
            for user in users:
                # Check if membership exists
                result = await db.execute(
                    select(RoomMember).where(
                        RoomMember.room_id == room.id,
                        RoomMember.user_id == user.id,
                    )
                )
                if result.scalar_one_or_none():
                    continue
                
                role = RoomRole.OWNER if user.id == room.owner_id else RoomRole.MEMBER
                member = RoomMember(
                    user_id=user.id,
                    room_id=room.id,
                    role=role,
                )
                db.add(member)
        
        await db.commit()
        
        # Create demo messages
        sample_messages = [
            "Hello everyone! 👋",
            "How's everyone doing today?",
            "This is a test message",
            "Welcome to the room!",
            "Let's discuss some interesting topics",
            "Has anyone tried the new features?",
            "Great to be here!",
            "Looking forward to chatting with you all",
        ]
        
        for room in rooms:
            # Check if messages already exist
            result = await db.execute(
                select(Message).where(Message.room_id == room.id).limit(1)
            )
            if result.scalar_one_or_none():
                continue
            
            # Create 10-20 messages per room
            num_messages = random.randint(10, 20)
            for i in range(num_messages):
                author = random.choice(users)
                content = random.choice(sample_messages)
                created_at = datetime.utcnow() - timedelta(
                    hours=random.randint(0, 24),
                    minutes=random.randint(0, 59),
                )
                
                message = Message(
                    room_id=room.id,
                    author_id=author.id,
                    content=content,
                    content_type="text",
                    created_at=created_at,
                )
                db.add(message)
        
        await db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(rooms)} rooms")
        print("Created messages in each room")
        print("\nYou can login with:")
        print("  Username: user1 (or user2, user3, etc.)")
        print("  Password: password123")


if __name__ == "__main__":
    asyncio.run(seed_database())



