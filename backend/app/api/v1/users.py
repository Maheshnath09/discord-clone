"""
User endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import os
import uuid
from pathlib import Path
from PIL import Image

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserPublic
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    if update_data.display_name is not None:
        current_user.display_name = update_data.display_name
    if update_data.bio is not None:
        current_user.bio = update_data.bio
    
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload user avatar to Supabase Storage."""
    from io import BytesIO
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes",
        )
    
    # Process image - resize for optimal storage
    try:
        img = Image.open(BytesIO(contents))
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize to max 400x400 for avatars
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Save to bytes with compression
        output = BytesIO()
        img.save(output, format='JPEG', optimize=True, quality=85)
        processed_data = output.getvalue()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not process image: {str(e)}",
        )
    
    # Generate unique filename
    filename = f"user_{current_user.id}_{uuid.uuid4()}.jpg"
    
    # Upload to Supabase Storage if configured
    if settings.USE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            from supabase import create_client
            
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Upload to Supabase Storage
            result = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                path=filename,
                file=processed_data,
                file_options={"content-type": "image/jpeg", "upsert": "true"}
            )
            
            # Get public URL
            avatar_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(filename)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to storage: {str(e)}",
            )
    else:
        # Fallback to local storage (for development)
        upload_dir = Path(settings.UPLOAD_DIR) / "avatars"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(processed_data)
        
        avatar_url = f"/uploads/avatars/{filename}"
    
    # Update user avatar URL
    current_user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get public user profile."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user



