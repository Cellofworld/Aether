"""
Playback routes for video streaming and progress tracking.

Provides endpoints for:
- Video streaming (direct play, transcoding)
- Playback session management
- Watch progress tracking
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import os
from pathlib import Path

from app.db.session import get_db
from app.models.user import User
from app.models.media import MediaItem, VideoFile
from app.models.playback_session import PlaybackSession
from app.models.watch_progress import WatchProgress
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


@router.get("/{media_id}/stream")
async def stream_media(
    media_id: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    direct_play: bool = Query(True),
) -> FileResponse:
    """
    Stream a media file.
    
    Supports direct play (original file) or transcoding.
    """
    # Get media item with video file
    query = select(MediaItem).where(MediaItem.id == media_id).options(
        # Add relationships if needed
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Get video file
    vf_query = select(VideoFile).where(VideoFile.media_id == media_id)
    vf_result = await db.execute(vf_query)
    video_file = vf_result.scalar_one_or_none()
    
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    # Check file exists
    if not os.path.exists(video_file.path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Create playback session
    session = PlaybackSession(
        user_id=current_user.id,
        media_id=media_id,
        device_info=request.headers.get("user-agent", "Unknown"),
    )
    db.add(session)
    await db.commit()
    
    # Return file with range support
    return FileResponse(
        path=video_file.path,
        media_type="video/mp4",
        filename=video_file.filename,
    )


@router.post("/session/start")
async def start_playback_session(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    media_id: str,
    device_info: Optional[str] = None,
) -> dict:
    """Start a new playback session."""
    session = PlaybackSession(
        user_id=current_user.id,
        media_id=media_id,
        device_info=device_info,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "session_id": session.id,
        "media_id": media_id,
        "started_at": session.started_at.isoformat(),
    }


@router.post("/session/{session_id}/progress")
async def update_playback_progress(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    position: int,
    duration: Optional[int] = None,
    paused: bool = False,
) -> dict:
    """Update playback progress for a session."""
    # Get session
    query = select(PlaybackSession).where(PlaybackSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update watch progress
    wp_query = select(WatchProgress).where(
        (WatchProgress.user_id == current_user.id) &
        (WatchProgress.media_id == session.media_id)
    )
    wp_result = await db.execute(wp_query)
    watch_progress = wp_result.scalar_one_or_none()
    
    if not watch_progress:
        watch_progress = WatchProgress(
            user_id=current_user.id,
            media_id=session.media_id,
        )
        db.add(watch_progress)
    
    watch_progress.position = position
    watch_progress.duration = duration or watch_progress.duration
    watch_progress.is_watching = not paused
    
    await db.commit()
    
    return {
        "session_id": session_id,
        "position": position,
        "duration": duration,
        "paused": paused,
    }


@router.post("/session/{session_id}/stop")
async def stop_playback_session(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    position: int,
    duration: Optional[int] = None,
) -> dict:
    """Stop a playback session and save final progress."""
    # Get session
    query = select(PlaybackSession).where(
        (PlaybackSession.id == session_id) &
        (PlaybackSession.user_id == current_user.id)
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # End session
    from datetime import datetime
    session.ended_at = datetime.utcnow()
    
    # Update watch progress
    wp_query = select(WatchProgress).where(
        (WatchProgress.user_id == current_user.id) &
        (WatchProgress.media_id == session.media_id)
    )
    wp_result = await db.execute(wp_query)
    watch_progress = wp_result.scalar_one_or_none()
    
    if not watch_progress:
        watch_progress = WatchProgress(
            user_id=current_user.id,
            media_id=session.media_id,
        )
        db.add(watch_progress)
    
    watch_progress.position = position
    watch_progress.duration = duration or watch_progress.duration
    watch_progress.is_watching = False
    
    # Mark as watched if > 90% complete
    if duration and position > duration * 0.9:
        watch_progress.watched = True
    
    await db.commit()
    
    return {
        "session_id": session_id,
        "ended_at": session.ended_at.isoformat(),
        "position": position,
        "watched": watch_progress.watched,
    }


@router.get("/resume")
async def get_resume_items(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
) -> list:
    """Get items that can be resumed."""
    query = select(WatchProgress).where(
        (WatchProgress.user_id == current_user.id) &
        (WatchProgress.watched == False) &
        (WatchProgress.position > 0)
    ).order_by(WatchProgress.updated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    progress_items = result.scalars().all()
    
    return [
        {
            "media_id": wp.media_id,
            "position": wp.position,
            "duration": wp.duration,
            "percent_complete": round((wp.position / wp.duration * 100), 1) if wp.duration else 0,
            "updated_at": wp.updated_at.isoformat() if wp.updated_at else None,
        }
        for wp in progress_items
    ]
