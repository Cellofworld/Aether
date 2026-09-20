"""
Search routes for finding media content.

Provides endpoints for:
- Full-text search across media library
- Filtered search by type, genre, year
- Search suggestions
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.media import MediaItem, MediaType
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def search(
    query: str = Query(..., min_length=1),
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    media_type: Optional[MediaType] = None,
    library_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
) -> dict:
    """
    Search for media items.
    
    Performs a full-text search on title and original_title.
    """
    search_query = select(MediaItem).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.movie),
        selectinload(MediaItem.series),
    )
    
    # Build search condition (case-insensitive partial match)
    search_pattern = f"%{query}%"
    search_condition = or_(
        MediaItem.title.ilike(search_pattern),
        MediaItem.original_title.ilike(search_pattern),
    )
    
    search_query = search_query.where(search_condition)
    
    # Apply filters
    if media_type:
        search_query = search_query.where(MediaItem.type == media_type)
        
    if library_id:
        search_query = search_query.where(MediaItem.library_id == library_id)
    
    # Limit results
    search_query = search_query.limit(limit)
    
    result = await db.execute(search_query)
    items = result.scalars().all()
    
    return {
        "query": query,
        "results": [_media_to_dict(item) for item in items],
        "total": len(items),
    }


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=1),
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    limit: int = Query(5, ge=1, le=10),
) -> List[str]:
    """
    Get search suggestions based on partial query.
    
    Returns matching titles for autocomplete.
    """
    search_pattern = f"{q}%"
    
    query = select(MediaItem.title).where(
        MediaItem.title.ilike(search_pattern)
    ).distinct().limit(limit)
    
    result = await db.execute(query)
    titles = result.scalars().all()
    
    return list(titles)


def _media_to_dict(item: MediaItem) -> dict:
    """Convert MediaItem to search result dictionary."""
    result = {
        "id": item.id,
        "type": item.type.value,
        "title": item.title,
        "year": item.year,
        "poster_path": item.poster_path,
        "backdrop_path": item.backdrop_path,
        "tmdb_id": item.tmdb_id,
    }
    
    # Add additional info based on type
    if item.movie:
        result["runtime"] = item.movie.runtime
        result["release_date"] = item.movie.release_date
        
    if item.series:
        result["number_of_seasons"] = item.series.number_of_seasons
        result["first_air_date"] = item.series.first_air_date
    
    # Add video quality badge info
    if item.video_files:
        vf = item.video_files[0]
        result["resolution"] = vf.resolution
        result["hdr"] = vf.hdr
    
    return result
