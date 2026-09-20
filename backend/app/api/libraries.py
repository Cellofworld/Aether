"""API router for media libraries."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.library import Library, LibraryPath
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.schemas.library import LibraryCreate, LibraryUpdate, LibraryResponse, LibraryPathResponse
from app.media.scanner import MediaScanner, get_scanner

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=List[LibraryResponse])
async def get_libraries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all libraries."""
    result = await db.execute(select(Library))
    libraries = result.scalars().all()
    return libraries


@router.post("", response_model=LibraryResponse)
async def create_library(
    library_data: LibraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    library = Library(
        name=library_data.name,
        type=library_data.type,
        description=library_data.description
    )
    
    db.add(library)
    await db.commit()
    await db.refresh(library)
    
    # Add paths if provided
    if library_data.paths:
        for path_str in library_data.paths:
            lib_path = LibraryPath(library_id=library.id, path=path_str)
            db.add(lib_path)
        
        await db.commit()
        await db.refresh(library)
    
    return library


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(
    library_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific library by ID."""
    result = await db.execute(select(Library).where(Library.id == library_id))
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    return library


@router.put("/{library_id}", response_model=LibraryResponse)
async def update_library(
    library_id: int,
    library_data: LibraryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(Library).where(Library.id == library_id))
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Update fields
    if library_data.name is not None:
        library.name = library_data.name
    if library_data.description is not None:
        library.description = library_data.description
    
    await db.commit()
    await db.refresh(library)
    
    return library


@router.delete("/{library_id}")
async def delete_library(
    library_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(Library).where(Library.id == library_id))
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    await db.delete(library)
    await db.commit()
    
    return {"message": "Library deleted"}


@router.post("/{library_id}/paths")
async def add_library_path(
    library_id: int,
    path_data: dict,  # {"path": "/media/movies"}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a path to a library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(Library).where(Library.id == library_id))
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    lib_path = LibraryPath(library_id=library.id, path=path_data["path"])
    db.add(lib_path)
    await db.commit()
    
    return {"message": "Path added"}


@router.delete("/{library_id}/paths/{path_id}")
async def remove_library_path(
    library_id: int,
    path_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a path from a library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(
        select(LibraryPath).where(
            LibraryPath.id == path_id,
            LibraryPath.library_id == library_id
        )
    )
    lib_path = result.scalar_one_or_none()
    
    if not lib_path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    await db.delete(lib_path)
    await db.commit()
    
    return {"message": "Path removed"}


@router.post("/{library_id}/scan")
async def scan_library(
    library_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start scanning a library. Admin only."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(select(Library).where(Library.id == library_id))
    library = result.scalar_one_or_none()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Start scan in background
    scanner = get_scanner(db)
    
    async def run_scan():
        try:
            await scanner.scan_library(library_id)
        except Exception as e:
            print(f"Scan failed: {e}")
    
    background_tasks.add_task(run_scan)
    
    return {"message": "Scan started", "library_id": library_id}


@router.get("/{library_id}/scan/progress")
async def get_scan_progress(
    library_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scan progress for a library."""
    scanner = get_scanner(db)
    progress = scanner.get_progress()
    
    return progress
