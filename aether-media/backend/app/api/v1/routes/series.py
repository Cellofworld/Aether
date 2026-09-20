"""
Series-specific routes.

Provides endpoints for:
- Listing series
- Getting series and episode details
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.media import MediaItem, MediaType
from app.models.series import Series, Season, Episode
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_series(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    library_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """Get paginated list of series."""
    query = select(MediaItem).where(MediaItem.type == MediaType.SERIES).options(
        selectinload(MediaItem.video_files),
        selectinload(MediaItem.series),
    )
    
    if library_id:
        query = query.where(MediaItem.library_id == library_id)
    
    offset = (page - 1) * page_size
    query = query.order_by(MediaItem.title).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    count_query = select(func.count(MediaItem.id)).where(MediaItem.type == MediaType.SERIES)
    if library_id:
        count_query = count_query.where(MediaItem.library_id == library_id)
    
    total = (await db.execute(count_query)).scalar() or 0
    
    return {
        "items": [_series_to_dict(s) for s in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{series_id}")
async def get_series(
    series_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get detailed series information with seasons and episodes."""
    query = select(MediaItem).where(
        (MediaItem.id == series_id) & (MediaItem.type == MediaType.SERIES)
    ).options(
        selectinload(MediaItem.series)
        .selectinload(Series.seasons)
        .selectinload(Season.episodes),
        selectinload(MediaItem.video_files),
    )
    
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Series not found")
    
    return _series_to_dict(item, detailed=True)


@router.get("/{series_id}/season/{season_number}")
async def get_season(
    series_id: str,
    season_number: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get season details with episodes."""
    # Get series
    series_result = await db.execute(
        select(Series).where(Series.media_id == series_id)
        .options(selectinload(Series.seasons).selectinload(Season.episodes))
    )
    series = series_result.scalar_one_or_none()
    
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    
    # Find season
    season = next((s for s in series.seasons if s.number == season_number), None)
    
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    return {
        "id": season.id,
        "series_id": series_id,
        "number": season.number,
        "title": season.title,
        "overview": season.overview,
        "air_date": season.air_date,
        "poster_path": season.poster_path,
        "episode_count": season.episode_count,
        "episodes": [
            {
                "id": e.id,
                "number": e.number,
                "absolute_number": e.absolute_number,
                "title": e.title,
                "overview": e.overview,
                "air_date": e.air_date,
                "still_path": e.still_path,
                "runtime": e.runtime,
            }
            for e in season.episodes
        ],
    }


@router.get("/episode/{episode_id}")
async def get_episode(
    episode_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get episode details."""
    query = select(Episode).where(Episode.id == episode_id).options(
        selectinload(Episode.media_item).selectinload(MediaItem.video_files)
    )
    
    result = await db.execute(query)
    episode = result.scalar_one_or_none()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    return {
        "id": episode.id,
        "media_id": episode.media_id,
        "season_id": episode.season_id,
        "number": episode.number,
        "absolute_number": episode.absolute_number,
        "title": episode.title,
        "overview": episode.overview,
        "air_date": episode.air_date,
        "runtime": episode.runtime,
        "still_path": episode.still_path,
        "guest_stars": episode.guest_stars,
    }


def _series_to_dict(item: MediaItem, detailed: bool = False) -> dict:
    result = {
        "id": item.id,
        "title": item.title,
        "year": item.year,
        "poster_path": item.poster_path,
        "backdrop_path": item.backdrop_path,
        "tmdb_id": item.tmdb_id,
        "metadata": item.metadata or {},
    }
    
    if detailed and item.series:
        result.update({
            "status": item.series.status,
            "first_air_date": item.series.first_air_date,
            "number_of_seasons": item.series.number_of_seasons,
            "number_of_episodes": item.series.number_of_episodes,
            "genres": item.series.genres,
            "created_by": item.series.created_by,
        })
        
        if item.series.seasons:
            result["seasons"] = [
                {
                    "id": s.id,
                    "number": s.number,
                    "title": s.title,
                    "episode_count": s.episode_count,
                    "air_date": s.air_date,
                }
                for s in item.series.seasons
            ]
    
    return result
