"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
            },
        )
        assert response.status_code == 201
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate_username():
    """Test registration with duplicate username."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register first user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test1@example.com",
                "username": "duplicate",
                "password": "testpass123",
            },
        )
        
        # Try to register with same username
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test2@example.com",
                "username": "duplicate",
                "password": "testpass123",
            },
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_login():
    """Test user login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "testpass123",
            },
        )
        
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": "loginuser",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": "nonexistent",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401



