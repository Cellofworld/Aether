"""
Media routes for accessing media library content.

Provides endpoints for:
- Listing media items
- Getting media details
- Filtering and searching
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.media import MediaItem, MediaType, VideoFile
from app.models.library import Library
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_media(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    library_id: Optional[str] = None,
    media_type: Optional[MediaType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """
    Get paginated list of media items.
    
    Can filter by library and media type.
    """
    query = select(MediaItem).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.movie),
        selectinload(MediaItem.series),
    )
    
    if library_id:
        query = query.where(MediaItem.library_id == library_id)
        
    if media_type:
        query = query.where(MediaItem.type == media_type)
    
    # Only get top-level items (movies and series)
    query = query.where(MediaItem.type.in_([MediaType.MOVIE, MediaType.SERIES]))
    
    # Order by title
    query = query.order_by(MediaItem.title)
    
    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(MediaItem.id)).where(
        MediaItem.type.in_([MediaType.MOVIE, MediaType.SERIES])
    )
    if library_id:
        count_query = count_query.where(MediaItem.library_id == library_id)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    return {
        "items": [_media_item_to_dict(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{media_id}")
async def get_media_item(
    media_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Get detailed information about a media item.
    """
    query = select(MediaItem).where(MediaItem.id == media_id).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.movie),
        selectinload(MediaItem.series).selectinload("seasons"),
        selectinload(MediaItem.genres),
        selectinload(MediaItem.persons),
    )
    
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media item not found",
        )
    
    return _media_item_to_dict(item, detailed=True)


@router.get("/{media_id}/file")
async def get_media_file(
    media_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Get the primary video file for a media item.
    """
    query = select(VideoFile).where(VideoFile.media_id == media_id)
    result = await db.execute(query)
    video_file = result.scalar_one_or_none()
    
    if not video_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found",
        )
    
    return {
        "id": video_file.id,
        "path": video_file.path,
        "filename": video_file.filename,
        "size": video_file.size,
        "duration": video_file.duration,
        "container": video_file.container,
        "video_codec": video_file.video_codec,
        "audio_codec": video_file.audio_codec,
        "resolution": video_file.resolution,
        "width": video_file.width,
        "height": video_file.height,
        "bitrate": video_file.bitrate,
        "framerate": video_file.framerate,
        "hdr": video_file.hdr,
        "audio_tracks": video_file.audio_tracks or [],
        "subtitle_tracks": video_file.subtitle_tracks or [],
    }


def _media_item_to_dict(item: MediaItem, detailed: bool = False) -> dict:
    """Convert MediaItem to dictionary."""
    result = {
        "id": item.id,
        "library_id": item.library_id,
        "type": item.type.value,
        "title": item.title,
        "original_title": item.original_title,
        "year": item.year,
        "poster_path": item.poster_path,
        "backdrop_path": item.backdrop_path,
        "tmdb_id": item.tmdb_id,
        "metadata": item.metadata or {},
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }
    
    if detailed:
        # Add video file info
        if item.video_files:
            vf = item.video_files[0]
            result["video_file"] = {
                "id": vf.id,
                "path": vf.path,
                "filename": vf.filename,
                "size": vf.size,
                "duration": vf.duration,
                "resolution": vf.resolution,
                "video_codec": vf.video_codec,
                "audio_codec": vf.audio_codec,
                "hdr": vf.hdr,
            }
        
        # Add movie-specific data
        if item.movie:
            result["movie"] = {
                "id": item.movie.id,
                "tmdb_id": item.movie.tmdb_id,
                "runtime": item.movie.runtime,
                "tagline": item.movie.tagline,
                "release_date": item.movie.release_date,
            }
        
        # Add series-specific data
        if item.series:
            result["series"] = {
                "id": item.series.id,
                "tmdb_id": item.series.tmdb_id,
                "status": item.series.status,
                "first_air_date": item.series.first_air_date,
                "number_of_seasons": item.series.number_of_seasons,
                "number_of_episodes": item.series.number_of_episodes,
                "seasons": [
                    {
                        "id": s.id,
                        "number": s.number,
                        "title": s.title,
                        "episode_count": s.episode_count,
                        "air_date": s.air_date,
                    }
                    for s in item.series.seasons
                ] if item.series.seasons else [],
            }
    
    return result
