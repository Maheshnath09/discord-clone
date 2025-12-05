"""
Utilities to seed demo data for local development.
"""
from datetime import datetime, timedelta
import random

from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.room import Room, RoomMember, RoomRole
from app.models.message import Message


async def ensure_demo_data():
    """
    Create demo users, rooms, and messages if the database is empty.
    """
    if not settings.AUTO_SEED_DEMO_DATA:
        return

    async with AsyncSessionLocal() as session:
        room_count = await session.scalar(select(func.count(Room.id)))
        if room_count and room_count > 0:
            return

        demo_users = [
            {
                "username": "randomshii",
                "email": "random@example.com",
                "display_name": "Random Shii",
                "bio": "Server owner who loves chatting.",
            },
            {
                "username": "test01",
                "email": "test01@example.com",
                "display_name": "Test User 01",
                "bio": "Frontend enthusiast.",
            },
            {
                "username": "test02",
                "email": "test02@example.com",
                "display_name": "Test User 02",
                "bio": "Backend tinkerer.",
            },
        ]

        users = {}
        for data in demo_users:
            result = await session.execute(
                select(User).where(User.username == data["username"])
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=data["username"],
                    email=data["email"],
                    password_hash=get_password_hash("password123"),
                    display_name=data["display_name"],
                    bio=data["bio"],
                    is_verified=True,
                )
                session.add(user)
                await session.flush()
            users[data["username"]] = user

        demo_rooms = [
            {
                "name": "General Chat",
                "description": "Hang out with everyone.",
                "is_public": True,
                "owner": "randomshii",
                "members": ["randomshii", "test01", "test02"],
            },
            {
                "name": "Indie Hackers",
                "description": "Discuss side projects and SaaS ideas.",
                "is_public": True,
                "owner": "test01",
                "members": ["test01", "randomshii"],
            },
            {
                "name": "Gaming Squad",
                "description": "Queue up and share memes.",
                "is_public": True,
                "owner": "test02",
                "members": ["test02", "randomshii"],
            },
            {
                "name": "Product Team",
                "description": "Private room for planning launches.",
                "is_public": False,
                "owner": "randomshii",
                "members": ["randomshii", "test01"],
            },
        ]

        sample_messages = [
            "Hey everyone! 👋",
            "Welcome to the server!",
            "What are you building today?",
            "Anyone up for a quick call?",
            "Check out this cool library I found.",
            "Shipping new features all week 🚀",
        ]

        for room_data in demo_rooms:
            owner = users[room_data["owner"]]
            result = await session.execute(
                select(Room).where(Room.name == room_data["name"])
            )
            room = result.scalar_one_or_none()
            if room:
                continue

            room = Room(
                name=room_data["name"],
                description=room_data["description"],
                is_public=room_data["is_public"],
                owner_id=owner.id,
            )
            session.add(room)
            await session.flush()

            for member_username in set(room_data["members"]):
                member_user = users.get(member_username)
                if not member_user:
                    continue
                role = RoomRole.OWNER if member_user.id == owner.id else RoomRole.MEMBER
                membership = RoomMember(
                    user_id=member_user.id,
                    room_id=room.id,
                    role=role,
                )
                session.add(membership)

            # Add a few demo messages to public rooms
            if room.is_public:
                for i in range(3):
                    author_username = random.choice(room_data["members"])
                    author = users[author_username]
                    message = Message(
                        room_id=room.id,
                        author_id=author.id,
                        content=random.choice(sample_messages),
                        content_type="text",
                        created_at=datetime.utcnow() - timedelta(minutes=10 - i),
                    )
                    session.add(message)

        await session.commit()



