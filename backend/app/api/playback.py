"""API router for playback and streaming."""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.media import Movie, Series, Episode, VideoFile
from app.models.user import User
from app.models.playback import WatchProgress, PlaybackSession
from app.api.deps import get_current_user
from app.services.streaming import StreamService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playback", tags=["playback"])


@router.post("/progress")
async def update_playback_progress(
    progress_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update playback progress.
    Expects: { media_id, position, duration, media_type }
    """
    media_id = progress_data.get("media_id")
    position = progress_data.get("position", 0)
    duration = progress_data.get("duration", 0)
    media_type = progress_data.get("media_type", "movie")
    
    if not media_id:
        raise HTTPException(status_code=400, detail="media_id required")
    
    # Find or create watch progress
    result = await db.execute(
        select(WatchProgress).where(
            WatchProgress.user_id == current_user.id,
            WatchProgress.media_id == media_id
        )
    )
    watch_progress = result.scalar_one_or_none()
    
    if not watch_progress:
        watch_progress = WatchProgress(
            user_id=current_user.id,
            media_id=media_id,
            media_type=media_type
        )
        db.add(watch_progress)
    
    # Update progress
    watch_progress.position = int(position)
    watch_progress.duration = int(duration)
    watch_progress.is_watched = (position / duration) > 0.9 if duration > 0 else False
    
    await db.commit()
    await db.refresh(watch_progress)
    
    return {"status": "ok", "position": position}


@router.get("/continue-watching")
async def get_continue_watching(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of items user is currently watching."""
    result = await db.execute(
        select(WatchProgress)
        .where(
            WatchProgress.user_id == current_user.id,
            WatchProgress.is_watched == False,
            WatchProgress.position > 0
        )
        .order_by(WatchProgress.updated_at.desc())
        .limit(20)
    )
    progresses = result.scalars().all()
    
    # Enrich with media details
    items = []
    for progress in progresses:
        item = {
            "progress": progress,
            "media": None
        }
        
        # Get media based on type
        if progress.media_type == "movie":
            media_result = await db.execute(
                select(Movie).where(Movie.id == progress.media_id)
            )
            item["media"] = media_result.scalar_one_or_none()
        elif progress.media_type == "episode":
            media_result = await db.execute(
                select(Episode).where(Episode.id == progress.media_id)
            )
            item["media"] = media_result.scalar_one_or_none()
        
        if item["media"]:
            items.append(item)
    
    return items


# Streaming endpoints
stream_service = StreamService()

@router.get("/stream/{media_id}")
async def stream_media(
    media_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stream media file with support for HTTP Range requests.
    Uses Direct Play when possible.
    """
    # Find the video file
    result = await db.execute(
        select(VideoFile).where(VideoFile.media_id == media_id)
    )
    video_file = result.scalar_one_or_none()
    
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    file_path = Path(video_file.path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Use streaming service to handle range requests
    return await stream_service.stream_file(request, file_path)


@router.get("/stream/{media_id}/master.m3u8")
async def get_hls_playlist(
    media_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get HLS master playlist for transcoding.
    Used when Direct Play is not supported.
    """
    # Find the video file
    result = await db.execute(
        select(VideoFile).where(VideoFile.media_id == media_id)
    )
    video_file = result.scalar_one_or_none()
    
    if not video_file:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    # Generate HLS playlist
    playlist = await stream_service.generate_hls_playlist(video_file, request)
    
    if not playlist:
        raise HTTPException(status_code=500, detail="Failed to generate HLS playlist")
    
    return Response(
        content=playlist,
        media_type="application/vnd.apple.mpegurl"
    )


@router.get("/stream/{media_id}/segment/{segment_id}.ts")
async def get_hls_segment(
    media_id: int,
    segment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get HLS segment for transcoding."""
    # This would serve pre-generated segments from transcode directory
    # For now, return placeholder
    raise HTTPException(status_code=501, detail="HLS transcoding not yet implemented")


@router.get("/subtitles/{track_id}")
async def get_subtitle(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subtitle file content."""
    from app.models.media import SubtitleTrack
    
    result = await db.execute(
        select(SubtitleTrack).where(SubtitleTrack.id == track_id)
    )
    subtitle = result.scalar_one_or_none()
    
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    
    if not subtitle.is_external or not subtitle.path:
        raise HTTPException(status_code=400, detail="External subtitle required")
    
    sub_path = Path(subtitle.path)
    if not sub_path.exists():
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    
    return FileResponse(
        path=sub_path,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={sub_path.name}"}
    )
