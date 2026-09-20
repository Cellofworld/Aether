"""API router for admin operations."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import text

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.library import Library
from app.models.media import Movie, Series, Episode, VideoFile
from app.api.deps import get_current_user
from app.media.scanner import get_scanner

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get counts
    movie_count = await db.execute(select(func.count()).select_from(Movie))
    series_count = await db.execute(select(func.count()).select_from(Series))
    episode_count = await db.execute(select(func.count()).select_from(Episode))
    library_count = await db.execute(select(func.count()).select_from(Library))
    file_count = await db.execute(select(func.count()).select_from(VideoFile))
    
    # Get total storage (sum of all video file sizes)
    result = await db.execute(select(func.sum(VideoFile.size)))
    total_storage = result.scalar() or 0
    
    return {
        "movies": movie_count.scalar(),
        "series": series_count.scalar(),
        "episodes": episode_count.scalar(),
        "libraries": library_count.scalar(),
        "files": file_count.scalar(),
        "storage_bytes": total_storage,
        "storage_formatted": _format_bytes(total_storage)
    }


@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return users


@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: dict,  # {"role": "admin" | "user"}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user role. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role_str = role_data.get("role", "user")
    try:
        user.role = UserRole(role_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    await db.commit()
    
    return {"message": "Role updated", "user_id": user_id, "role": role_str}


@router.get("/scanner/status")
async def get_scanner_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scanner status. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    scanner = get_scanner(db)
    progress = scanner.get_progress()
    
    return {
        "is_running": scanner.is_running,
        "progress": progress
    }


@router.post("/scan-all")
async def scan_all_libraries(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start scanning all libraries. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(Library))
    libraries = result.scalars().all()
    
    scanner = get_scanner(db)
    
    async def run_scans():
        for library in libraries:
            try:
                await scanner.scan_library(library.id)
            except Exception as e:
                print(f"Scan failed for library {library.id}: {e}")
    
    background_tasks.add_task(run_scans)
    
    return {"message": f"Scan started for {len(libraries)} libraries"}


def _format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_value) < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"
