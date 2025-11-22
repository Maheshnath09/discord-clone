"""
Tests for room endpoints.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_room():
    """Test room creation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "roomowner@example.com",
                "username": "roomowner",
                "password": "testpass123",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": "roomowner",
                "password": "testpass123",
            },
        )
        token = login_response.json()["access_token"]
        
        # Create room
        response = await client.post(
            "/api/v1/rooms",
            json={
                "name": "Test Room",
                "description": "A test room",
                "is_public": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Room"


@pytest.mark.asyncio
async def test_list_rooms():
    """Test listing rooms."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/rooms")
        assert response.status_code == 200
        assert isinstance(response.json(), list)



