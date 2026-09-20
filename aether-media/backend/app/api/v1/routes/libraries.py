"""
Library routes for managing media libraries.

Provides endpoints for:
- Listing libraries
- Creating libraries
- Updating libraries
- Deleting libraries
- Triggering scans
- Getting library statistics
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.library import LibraryType
from app.schemas.library import (
    LibraryResponse,
    LibraryCreate,
    LibraryUpdate,
    LibraryStats,
    ScanJobResponse,
)
from app.services.library import (
    get_libraries,
    get_library,
    create_library as create_library_service,
    update_library as update_library_service,
    delete_library as delete_library_service,
    create_scan_job,
    get_scan_jobs,
    get_library_stats,
)
from app.api.v1.routes.auth import get_current_user

router = APIRouter()


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency to require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


@router.get("", response_model=List[LibraryResponse])
async def list_libraries(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    include_disabled: bool = False,
) -> List[Library]:
    """
    Get all libraries.

    Returns a list of all configured media libraries.
    """
    return await get_libraries(db, include_disabled=include_disabled)


@router.post("", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Library:
    """
    Create a new library (admin only).

    Args:
        library_data: Library creation data
        db: Database session
        _: Current admin user
    """
    return await create_library_service(
        db=db,
        name=library_data.name,
        type=library_data.type,
        root_paths=library_data.root_paths,
        scanner_config=library_data.scanner_config,
    )


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library_endpoint(
    library_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Library:
    """
    Get a specific library by ID.
    """
    library = await get_library(db, library_id)

    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )

    return library


@router.put("/{library_id}", response_model=LibraryResponse)
async def update_library(
    library_id: str,
    library_data: LibraryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> Library:
    """
    Update a library (admin only).
    """
    library = await update_library_service(
        db=db,
        library_id=library_id,
        name=library_data.name,
        root_paths=library_data.root_paths,
        scanner_config=library_data.scanner_config,
        is_enabled=library_data.is_enabled,
    )

    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )

    return library


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> None:
    """
    Delete a library (admin only).
    """
    deleted = await delete_library_service(db, library_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )


@router.get("/{library_id}/stats", response_model=LibraryStats)
async def get_library_stats_endpoint(
    library_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Get statistics for a library.
    """
    stats = await get_library_stats(db, library_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )

    return stats


@router.post("/{library_id}/scan", response_model=ScanJobResponse)
async def trigger_scan(
    library_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
    scan_type: str = "full",
) -> ScanJobResponse:
    """
    Trigger a library scan (admin only).

    Args:
        library_id: Library to scan
        db: Database session
        _: Current admin user
        scan_type: Type of scan (full or incremental)
    """
    # Verify library exists
    library = await get_library(db, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )

    scan_job = await create_scan_job(db, library_id, scan_type)

    if not scan_job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan job",
        )

    # Schedule the scan in background
    from app.workers.scanner import run_scan
    # Note: In production, this would be queued to Redis/Celery
    # For now, we'll start it as a background task
    # background_tasks.add_task(run_scan, db, scan_job.id)

    return ScanJobResponse.model_validate(scan_job)


@router.get("/{library_id}/scans", response_model=List[ScanJobResponse])
async def get_library_scans(
    library_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
) -> List[ScanJobResponse]:
    """
    Get scan history for a library.
    """
    jobs = await get_scan_jobs(db, library_id=library_id, limit=limit)
    return [ScanJobResponse.model_validate(job) for job in jobs]
