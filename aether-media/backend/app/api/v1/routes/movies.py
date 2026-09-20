"""
Movie-specific routes.

Provides endpoints for:
- Listing movies
- Getting movie details
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.media import MediaItem, MediaType
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_movies(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    library_id: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """Get paginated list of movies."""
    query = select(MediaItem).where(MediaItem.type == MediaType.MOVIE).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.movie),
    )
    
    if library_id:
        query = query.where(MediaItem.library_id == library_id)
        
    if year:
        query = query.where(MediaItem.year == year)
    
    offset = (page - 1) * page_size
    query = query.order_by(MediaItem.title).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    count_query = select(func.count(MediaItem.id)).where(MediaItem.type == MediaType.MOVIE)
    if library_id:
        count_query = count_query.where(MediaItem.library_id == library_id)
    if year:
        count_query = count_query.where(MediaItem.year == year)
    
    total = (await db.execute(count_query)).scalar() or 0
    
    return {
        "items": [_movie_to_dict(m) for m in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{movie_id}")
async def get_movie(
    movie_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get detailed movie information."""
    query = select(MediaItem).where(
        (MediaItem.id == movie_id) & (MediaItem.type == MediaType.MOVIE)
    ).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.movie),
        selectinload(MediaItem.genres),
        selectinload(MediaItem.persons),
    )
    
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return _movie_to_dict(item, detailed=True)


def _movie_to_dict(item: MediaItem, detailed: bool = False) -> dict:
    result = {
        "id": item.id,
        "title": item.title,
        "original_title": item.original_title,
        "year": item.year,
        "poster_path": item.poster_path,
        "backdrop_path": item.backdrop_path,
        "tmdb_id": item.tmdb_id,
        "metadata": item.metadata or {},
    }
    
    if detailed and item.movie:
        result.update({
            "runtime": item.movie.runtime,
            "tagline": item.movie.tagline,
            "release_date": item.movie.release_date,
            "genres": item.movie.genres,
        })
    
    if item.video_files:
        vf = item.video_files[0]
        result["video_file"] = {
            "resolution": vf.resolution,
            "video_codec": vf.video_codec,
            "hdr": vf.hdr,
        }
    
    return result
