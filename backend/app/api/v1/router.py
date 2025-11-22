"""
Main API router that includes all v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, rooms, messages, websockets

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(messages.router, prefix="/rooms", tags=["messages"])
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])



