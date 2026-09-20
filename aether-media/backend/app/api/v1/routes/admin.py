"""
Admin routes for system administration.

Provides endpoints for:
- Dashboard statistics
- System information
- Job management
- Settings management
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.library import Library
from app.models.media import MediaItem, VideoFile
from app.models.scan_job import ScanJob, ScanStatus
from app.models.playback_session import PlaybackSession
from app.models.watch_progress import WatchProgress
from app.api.v1.routes.auth import get_current_user
from app.services.library import get_scan_jobs, update_scan_job

router = APIRouter()


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency to require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


@router.get("/dashboard")
async def get_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> dict:
    """
    Get dashboard statistics.
    
    Returns overview of system status and media counts.
    """
    # Count libraries
    lib_count = await db.scalar(select(func.count(Library.id)))
    
    # Count media by type
    movie_count = await db.scalar(
        select(func.count(MediaItem.id)).where(MediaItem.type == "movie")
    )
    series_count = await db.scalar(
        select(func.count(MediaItem.id)).where(MediaItem.type == "series")
    )
    season_count = await db.scalar(
        select(func.count(MediaItem.id)).where(MediaItem.type == "season")
    )
    episode_count = await db.scalar(
        select(func.count(MediaItem.id)).where(MediaItem.type == "episode")
    )
    
    # Count video files
    file_count = await db.scalar(select(func.count(VideoFile.id)))
    
    # Count users
    user_count = await db.scalar(select(func.count(User.id)))
    
    # Get active playback sessions
    active_streams = await db.scalar(
        select(func.count(PlaybackSession.id)).where(
            PlaybackSession.ended_at.is_(None)
        )
    )
    
    # Get recent scan jobs
    recent_scans = await db.execute(
        select(ScanJob)
        .order_by(ScanJob.created_at.desc())
        .limit(5)
    )
    scans = recent_scans.scalars().all()
    
    # Calculate total storage (approximate from file sizes)
    storage_result = await db.execute(
        select(func.sum(VideoFile.size))
    )
    total_storage = storage_result.scalar() or 0
    
    return {
        "libraries": lib_count or 0,
        "movies": movie_count or 0,
        "series": series_count or 0,
        "seasons": season_count or 0,
        "episodes": episode_count or 0,
        "total_items": (movie_count or 0) + (series_count or 0) + (season_count or 0) + (episode_count or 0),
        "video_files": file_count or 0,
        "users": user_count or 0,
        "active_streams": active_streams or 0,
        "storage_bytes": total_storage,
        "storage_formatted": _format_bytes(total_storage),
        "recent_scans": [
            {
                "id": s.id,
                "library_id": s.library_id,
                "status": s.status.value,
                "progress": s.progress,
                "items_added": s.items_added,
                "items_updated": s.items_updated,
                "created_at": s.created_at.isoformat(),
            }
            for s in scans
        ],
    }


@router.get("/jobs")
async def get_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
    limit: int = 20,
) -> List[dict]:
    """
    Get recent scan jobs.
    """
    jobs = await get_scan_jobs(db, limit=limit)
    
    return [
        {
            "id": job.id,
            "library_id": job.library_id,
            "status": job.status.value,
            "progress": job.progress,
            "items_scanned": job.items_scanned,
            "items_added": job.items_added,
            "items_updated": job.items_updated,
            "items_removed": job.items_removed,
            "current_file": job.current_file,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat(),
        }
        for job in jobs
    ]


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> dict:
    """
    Cancel a running scan job.
    """
    job = await update_scan_job(
        db, job_id,
        status=ScanStatus.CANCELLED,
        error_message="Cancelled by user",
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return {"message": "Job cancelled", "job_id": job_id}


@router.get("/system")
async def get_system_info(
    _: Annotated[User, Depends(require_admin)],
) -> dict:
    """
    Get system information.
    """
    import platform
    import os
    
    # Get CPU info
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
    except ImportError:
        cpu_percent = 0
        memory = type('obj', (object,), {'percent': 0, 'total': 0, 'available': 0})()
        disk = type('obj', (object,), {'total': 0, 'used': 0, 'free': 0})()
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_percent": cpu_percent,
        "memory_total": memory.total,
        "memory_available": memory.available,
        "memory_percent": memory.percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "disk_percent": disk.percent,
    }


def _format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_value) < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"
