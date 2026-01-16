"""
Database configuration and session management.
"""
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def clean_asyncpg_url(database_url: str) -> tuple[str, dict]:
    """
    Clean database URL for asyncpg compatibility.
    Neon and other providers use libpq parameters that asyncpg doesn't support.
    Returns (cleaned_url, connect_args)
    """
    # Parameters that asyncpg doesn't support (from libpq)
    unsupported_params = {
        'sslmode', 'channel_binding', 'client_encoding', 
        'connect_timeout', 'application_name', 'options',
        'sslcert', 'sslkey', 'sslrootcert'
    }
    
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    
    # Check if we need SSL
    needs_ssl = False
    if 'sslmode' in query_params:
        sslmode = query_params['sslmode'][0]
        needs_ssl = sslmode in ('require', 'verify-ca', 'verify-full')
    if 'ssl' in query_params:
        needs_ssl = query_params['ssl'][0] in ('require', 'true', 'True')
    
    # Remove unsupported parameters
    cleaned_params = {k: v for k, v in query_params.items() if k not in unsupported_params and k != 'ssl'}
    
    # Rebuild the URL without unsupported params
    new_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    # Set up connect_args for SSL if needed
    connect_args = {}
    if needs_ssl:
        # Create SSL context for asyncpg
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context
    
    return cleaned_url, connect_args


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
    # PostgreSQL with asyncpg - clean URL and get connect_args
    db_url, pg_connect_args = clean_asyncpg_url(settings.DATABASE_URL)
    
    engine = create_async_engine(
        db_url,
        echo=settings.ENVIRONMENT == "development",
        connect_args=pg_connect_args,
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

