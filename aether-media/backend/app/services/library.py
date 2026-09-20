"""
Library service for managing media libraries.

Provides business logic for:
- Creating and updating libraries
- Scanning library content
- Managing library paths
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.library import Library, LibraryType
from app.models.media import MediaItem
from app.models.scan_job import ScanJob, ScanStatus

logger = logging.getLogger(__name__)


async def get_libraries(
    db: AsyncSession,
    include_disabled: bool = False,
) -> List[Library]:
    """
    Get all libraries.

    Args:
        db: Database session
        include_disabled: Whether to include disabled libraries

    Returns:
        List of libraries
    """
    query = select(Library).options(selectinload(Library.media_items))

    if not include_disabled:
        query = query.where(Library.is_enabled == True)

    query = query.order_by(Library.name)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_library(db: AsyncSession, library_id: str) -> Optional[Library]:
    """
    Get a library by ID.

    Args:
        db: Database session
        library_id: Library ID

    Returns:
        Library if found, None otherwise
    """
    query = select(Library).where(Library.id == library_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_library(
    db: AsyncSession,
    name: str,
    type: LibraryType,
    root_paths: List[str],
    scanner_config: Optional[dict] = None,
) -> Library:
    """
    Create a new library.

    Args:
        db: Database session
        name: Library name
        type: Library type
        root_paths: List of root directory paths
        scanner_config: Optional scanner configuration

    Returns:
        Created library
    """
    library = Library(
        name=name,
        type=type,
        root_paths=root_paths,
        scanner_config=scanner_config or {},
        is_enabled=True,
    )

    db.add(library)
    await db.commit()
    await db.refresh(library)

    logger.info(f"Created library: {library.name} (type={library.type})")

    return library


async def update_library(
    db: AsyncSession,
    library_id: str,
    name: Optional[str] = None,
    root_paths: Optional[List[str]] = None,
    scanner_config: Optional[dict] = None,
    is_enabled: Optional[bool] = None,
) -> Optional[Library]:
    """
    Update an existing library.

    Args:
        db: Database session
        library_id: Library ID
        name: New name
        root_paths: New root paths
        scanner_config: New scanner configuration
        is_enabled: Enable/disable flag

    Returns:
        Updated library if found, None otherwise
    """
    library = await get_library(db, library_id)

    if not library:
        return None

    if name is not None:
        library.name = name

    if root_paths is not None:
        library.root_paths = root_paths

    if scanner_config is not None:
        library.scanner_config = scanner_config

    if is_enabled is not None:
        library.is_enabled = is_enabled

    await db.commit()
    await db.refresh(library)

    logger.info(f"Updated library: {library.name}")

    return library


async def delete_library(db: AsyncSession, library_id: str) -> bool:
    """
    Delete a library.

    Args:
        db: Database session
        library_id: Library ID

    Returns:
        True if deleted, False if not found
    """
    library = await get_library(db, library_id)

    if not library:
        return False

    await db.delete(library)
    await db.commit()

    logger.info(f"Deleted library: {library.name}")

    return True


async def create_scan_job(
    db: AsyncSession,
    library_id: str,
    scan_type: str = "full",
) -> Optional[ScanJob]:
    """
    Create a new scan job for a library.

    Args:
        db: Database session
        library_id: Library ID to scan
        scan_type: Type of scan (full, incremental)

    Returns:
        Created scan job, or None if library not found
    """
    library = await get_library(db, library_id)

    if not library:
        return None

    # Check for existing active scan
    existing_query = select(ScanJob).where(
        (ScanJob.library_id == library_id) &
        (ScanJob.status.in_([ScanStatus.PENDING, ScanStatus.RUNNING]))
    )
    result = await db.execute(existing_query)
    existing = result.scalar_one_or_none()

    if existing:
        logger.info(f"Scan already in progress for library {library.name}")
        return existing

    scan_job = ScanJob(
        library_id=library_id,
        scan_type=scan_type,
        status=ScanStatus.PENDING,
        progress=0,
    )

    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)

    logger.info(f"Created scan job for library: {library.name}")

    return scan_job


async def get_scan_jobs(
    db: AsyncSession,
    library_id: Optional[str] = None,
    limit: int = 10,
) -> List[ScanJob]:
    """
    Get scan jobs, optionally filtered by library.

    Args:
        db: Database session
        library_id: Optional library ID filter
        limit: Maximum number of results

    Returns:
        List of scan jobs
    """
    query = select(ScanJob).order_by(ScanJob.created_at.desc()).limit(limit)

    if library_id:
        query = query.where(ScanJob.library_id == library_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_scan_job(
    db: AsyncSession,
    job_id: str,
    status: Optional[ScanStatus] = None,
    progress: Optional[int] = None,
    current_file: Optional[str] = None,
    items_added: Optional[int] = None,
    items_updated: Optional[int] = None,
    items_removed: Optional[int] = None,
    errors: Optional[List[str]] = None,
    error_message: Optional[str] = None,
) -> Optional[ScanJob]:
    """
    Update a scan job's status.

    Args:
        db: Database session
        job_id: Scan job ID
        status: New status
        progress: Progress percentage (0-100)
        current_file: Currently processing file
        items_added: Count of added items
        items_updated: Count of updated items
        items_removed: Count of removed items
        errors: List of error messages
        error_message: General error message

    Returns:
        Updated scan job if found, None otherwise
    """
    query = select(ScanJob).where(ScanJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        return None

    if status is not None:
        job.status = status

    if progress is not None:
        job.progress = min(100, max(0, progress))

    if current_file is not None:
        job.current_file = current_file

    if items_added is not None:
        job.items_added = items_added

    if items_updated is not None:
        job.items_updated = items_updated

    if items_removed is not None:
        job.items_removed = items_removed

    if errors is not None:
        job.errors = errors

    if error_message is not None:
        job.error_message = error_message

    if status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
        job.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(job)

    return job


async def get_library_stats(db: AsyncSession, library_id: str) -> dict:
    """
    Get statistics for a library.

    Args:
        db: Database session
        library_id: Library ID

    Returns:
        Dictionary with library statistics
    """
    from sqlalchemy import func

    library = await get_library(db, library_id)

    if not library:
        return {}

    # Count media items by type
    movie_count = await db.scalar(
        select(func.count(MediaItem.id)).where(
            (MediaItem.library_id == library_id) &
            (MediaItem.type == "movie")
        )
    )

    series_count = await db.scalar(
        select(func.count(MediaItem.id)).where(
            (MediaItem.library_id == library_id) &
            (MediaItem.type == "series")
        )
    )

    season_count = await db.scalar(
        select(func.count(MediaItem.id)).where(
            (MediaItem.library_id == library_id) &
            (MediaItem.type == "season")
        )
    )

    episode_count = await db.scalar(
        select(func.count(MediaItem.id)).where(
            (MediaItem.library_id == library_id) &
            (MediaItem.type == "episode")
        )
    )

    return {
        "id": library_id,
        "name": library.name,
        "type": library.type.value,
        "movies": movie_count or 0,
        "series": series_count or 0,
        "seasons": season_count or 0,
        "episodes": episode_count or 0,
        "total_items": (movie_count or 0) + (series_count or 0) + (season_count or 0) + (episode_count or 0),
    }
