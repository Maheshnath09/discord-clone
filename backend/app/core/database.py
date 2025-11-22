"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# For SQLite, we need special handling
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite async requires special setup
    connect_args = {"check_same_thread": False}
    engine = create_async_engine(
        settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
        echo=settings.ENVIRONMENT == "development",
        connect_args=connect_args,
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other databases
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.ENVIRONMENT == "development",
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    # Import all models to register them with Base
    from app.models.user import User, RefreshToken
    from app.models.room import Room, RoomMember
    from app.models.message import Message, MessageReaction
    from app.models.attachment import Attachment
    from app.models.audit_log import AuditLog
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    if settings.AUTO_SEED_DEMO_DATA:
        from app.db.seed import ensure_demo_data
        await ensure_demo_data()

