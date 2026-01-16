"""
FastAPI application entry point for Discord-like chat app.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, init_db
from app.api.v1.router import api_router
from app.websockets.manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await init_db()
    await websocket_manager.initialize()
    yield
    # Shutdown
    await websocket_manager.cleanup()


app = FastAPI(
    title="Discord-like Chat API",
    description="Production-ready real-time chat application API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware - use dynamic origins for production support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (for production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve static files (uploads)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Discord-like Chat API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug/cors")
async def cors_debug():
    """Debug endpoint to check CORS configuration."""
    return {
        "cors_origins": settings.get_cors_origins(),
        "frontend_url": settings.FRONTEND_URL,
        "allowed_origins_env": settings.ALLOWED_ORIGINS,
    }


@app.get("/debug/websocket")
async def websocket_debug():
    """Debug endpoint to check WebSocket connection status."""
    stats = websocket_manager.get_connection_stats()
    return {
        "websocket_stats": stats,
        "message": "Use this to verify WebSocket connections are being tracked"
    }


@app.post("/debug/broadcast/{room_id}")
async def test_broadcast(room_id: int, message: str = "Test broadcast message"):
    """Debug endpoint to manually trigger a broadcast to a room."""
    print(f"[DEBUG] Test broadcast triggered for room {room_id}")
    broadcast_payload = {
        "type": "message.create",
        "data": {
            "id": 999999,
            "room_id": room_id,
            "content": message,
            "author_id": 0,
            "author": {"id": 0, "username": "SYSTEM", "display_name": "System Test"},
            "created_at": "2024-01-01T00:00:00",
        }
    }
    await websocket_manager.broadcast_to_room(room_id, broadcast_payload)
    return {"status": "broadcast_sent", "room_id": room_id, "message": message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )

