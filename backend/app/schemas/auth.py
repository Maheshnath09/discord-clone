"""
Authentication schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    identifier: str  # Can be email or username
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None



