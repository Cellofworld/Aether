"""API router for search functionality."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.media import Movie, Series, Episode
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=dict)
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Global search across media library.
    Searches in titles, original titles, and descriptions.
    """
    search_term = f"%{q}%"
    
    results = {
        "movies": [],
        "series": [],
        "episodes": [],
        "query": q
    }
    
    # Search movies
    movie_query = (
        select(Movie)
        .where(
            or_(
                Movie.title.ilike(search_term),
                Movie.original_title.ilike(search_term)
            )
        )
        .limit(limit)
    )
    movie_result = await db.execute(movie_query)
    results["movies"] = movie_result.scalars().all()
    
    # Search series
    series_query = (
        select(Series)
        .where(
            or_(
                Series.title.ilike(search_term),
                Series.original_title.ilike(search_term)
            )
        )
        .limit(limit)
    )
    series_result = await db.execute(series_query)
    results["series"] = series_result.scalars().all()
    
    # Search episodes
    episode_query = (
        select(Episode)
        .where(
            or_(
                Episode.title.ilike(search_term),
                Episode.original_title.ilike(search_term)
            )
        )
        .limit(limit)
    )
    episode_result = await db.execute(episode_query)
    results["episodes"] = episode_result.scalars().all()
    
    return results
