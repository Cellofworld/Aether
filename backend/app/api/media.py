"""API router for media content (movies, series, episodes)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.media import Movie, Series, Season, Episode, MediaItem
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/movies", response_model=List[dict])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    library_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of movies with pagination."""
    query = select(Movie).options(selectinload(Movie.video_files))
    
    if library_id:
        query = query.where(Movie.library_id == library_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    movies = result.scalars().all()
    
    return movies


@router.get("/movies/{movie_id}", response_model=dict)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific movie by ID."""
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.video_files))
        .where(Movie.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return movie


@router.get("/series", response_model=List[dict])
async def get_series(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    library_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of series with pagination."""
    query = select(Series).options(selectinload(Series.seasons))
    
    if library_id:
        query = query.where(Series.library_id == library_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    series_list = result.scalars().all()
    
    return series_list


@router.get("/series/{series_id}", response_model=dict)
async def get_series(
    series_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific series by ID with seasons and episodes."""
    result = await db.execute(
        select(Series)
        .options(
            selectinload(Series.seasons).selectinload(Season.episodes)
        )
        .where(Series.id == series_id)
    )
    series = result.scalar_one_or_none()
    
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    
    return series


@router.get("/series/{series_id}/seasons", response_model=List[dict])
async def get_seasons(
    series_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all seasons for a series."""
    result = await db.execute(
        select(Season)
        .options(selectinload(Season.episodes))
        .where(Season.series_id == series_id)
        .order_by(Season.season_number)
    )
    seasons = result.scalars().all()
    
    return seasons


@router.get("/seasons/{season_id}/episodes", response_model=List[dict])
async def get_episodes(
    season_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all episodes for a season."""
    result = await db.execute(
        select(Episode)
        .options(selectinload(Episode.video_files))
        .where(Episode.season_id == season_id)
        .order_by(Episode.episode_number)
    )
    episodes = result.scalars().all()
    
    return episodes


@router.get("/episodes/{episode_id}", response_model=dict)
async def get_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific episode by ID."""
    result = await db.execute(
        select(Episode)
        .options(selectinload(Episode.video_files))
        .where(Episode.id == episode_id)
    )
    episode = result.scalar_one_or_none()
    
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    return episode
