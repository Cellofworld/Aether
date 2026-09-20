"""
Media scanner worker for scanning library content.

Scans library directories, identifies media files, parses metadata,
and updates the database.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.library import Library
from app.models.media import MediaItem, MediaType, VideoFile
from app.models.scan_job import ScanJob, ScanStatus
from app.services.library import update_scan_job
from app.core.config import settings

logger = logging.getLogger(__name__)


class MediaScanner:
    """
    Media scanner for processing library content.
    
    Scans directories for media files and creates/updates database entries.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_extensions = settings.video_extensions_list
        self.min_file_size = settings.MIN_FILE_SIZE
        
    async def scan_library(self, job_id: str) -> None:
        """
        Scan a library based on a scan job.
        
        Args:
            job_id: The scan job ID to process
        """
        # Get the scan job
        job_result = await self.db.execute(
            select(ScanJob).where(ScanJob.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job:
            logger.error(f"Scan job {job_id} not found")
            return
            
        # Get the library
        lib_result = await self.db.execute(
            select(Library).where(Library.id == job.library_id)
        )
        library = lib_result.scalar_one_or_none()
        
        if not library:
            logger.error(f"Library {job.library_id} not found")
            await update_scan_job(
                self.db, job_id,
                status=ScanStatus.FAILED,
                error_message="Library not found",
            )
            return
            
        if not library.is_enabled:
            logger.info(f"Library {library.name} is disabled, skipping scan")
            return
            
        # Update job status to running
        await update_scan_job(
            self.db, job_id,
            status=ScanStatus.RUNNING,
            started_at=datetime.utcnow(),
            progress=0,
        )
        
        try:
            # Scan each root path
            root_paths = library.root_paths or []
            total_paths = len(root_paths)
            
            items_added = 0
            items_updated = 0
            items_removed = 0
            errors = []
            
            for idx, root_path in enumerate(root_paths):
                if not os.path.exists(root_path):
                    logger.warning(f"Root path does not exist: {root_path}")
                    errors.append({
                        "path": root_path,
                        "error": "Path does not exist",
                    })
                    continue
                    
                logger.info(f"Scanning root path: {root_path}")
                
                # Calculate progress
                progress = int((idx / total_paths) * 100) if total_paths > 0 else 0
                
                await update_scan_job(
                    self.db, job_id,
                    progress=progress,
                    current_file=f"Scanning: {root_path}",
                )
                
                # Scan this path
                result = await self._scan_directory(
                    root_path,
                    library.id,
                    library.type.value,
                )
                
                items_added += result["added"]
                items_updated += result["updated"]
                items_removed += result["removed"]
                errors.extend(result["errors"])
                
            # Mark job as complete
            await update_scan_job(
                self.db, job_id,
                status=ScanStatus.COMPLETED,
                progress=100,
                items_added=items_added,
                items_updated=items_updated,
                items_removed=items_removed,
                errors=errors[:100],  # Limit stored errors
            )
            
            logger.info(
                f"Scan completed for library {library.name}: "
                f"+{items_added} ~{items_updated} -{items_removed}"
            )
            
        except Exception as e:
            logger.exception(f"Scan failed for library {library.name}: {e}")
            await update_scan_job(
                self.db, job_id,
                status=ScanStatus.FAILED,
                error_message=str(e),
            )
    
    async def _scan_directory(
        self,
        root_path: str,
        library_id: str,
        library_type: str,
    ) -> Dict[str, Any]:
        """
        Scan a directory recursively for media files.
        
        Args:
            root_path: Root directory to scan
            library_id: Library ID to associate files with
            library_type: Type of library (movies, series, etc.)
            
        Returns:
            Dictionary with counts of added, updated, removed items
        """
        added = 0
        updated = 0
        removed = 0
        errors = []
        
        # Collect all video files
        video_files = []
        
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Skip hidden directories
                dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                        
                    # Check extension
                    ext = os.path.splitext(filename)[1].lower().lstrip('.')
                    if ext not in self.video_extensions:
                        continue
                    
                    filepath = os.path.join(dirpath, filename)
                    
                    # Check file size
                    try:
                        size = os.path.getsize(filepath)
                        if size < self.min_file_size:
                            logger.debug(f"Skipping small file: {filepath}")
                            continue
                    except OSError as e:
                        logger.warning(f"Cannot access file {filepath}: {e}")
                        errors.append({
                            "file": filepath,
                            "error": str(e),
                        })
                        continue
                    
                    video_files.append({
                        "path": filepath,
                        "filename": filename,
                        "size": size,
                        "relative_path": os.path.relpath(filepath, root_path),
                    })
                    
        except Exception as e:
            logger.exception(f"Error scanning directory {root_path}: {e}")
            errors.append({
                "path": root_path,
                "error": str(e),
            })
            
        # Process found files
        total_files = len(video_files)
        
        for idx, file_info in enumerate(video_files):
            try:
                # Update progress
                progress_offset = int((idx / total_files) * 20) if total_files > 0 else 0
                
                await update_scan_job(
                    self.db, 
                    getattr(self, '_current_job_id', None),
                    progress=progress_offset,
                    current_file=file_info["filename"],
                )
                
                # Parse filename to extract metadata
                parsed = self._parse_filename(file_info["filename"])
                
                # Check if file already exists
                existing = await self.db.execute(
                    select(VideoFile).where(VideoFile.path == file_info["path"])
                )
                video_file = existing.scalar_one_or_none()
                
                if video_file:
                    # Update existing file
                    updated += 1
                else:
                    # Create new media item and video file
                    await self._create_media_item(
                        library_id=library_id,
                        library_type=library_type,
                        file_info=file_info,
                        parsed=parsed,
                    )
                    added += 1
                    
            except Exception as e:
                logger.exception(f"Error processing file {file_info['path']}: {e}")
                errors.append({
                    "file": file_info["path"],
                    "error": str(e),
                })
        
        return {
            "added": added,
            "updated": updated,
            "removed": removed,
            "errors": errors,
        }
    
    def _parse_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse a filename to extract metadata.
        
        Supports various naming conventions:
        - Movie.Name.2024.1080p.mkv
        - Show.Name.S01E01.1080p.mkv
        - Show.Name.1x01.Episode.Name.mkv
        
        Args:
            filename: The filename to parse
            
        Returns:
            Dictionary with parsed metadata
        """
        import re
        
        name_without_ext = os.path.splitext(filename)[0]
        
        result = {
            "title": name_without_ext,
            "year": None,
            "season": None,
            "episode": None,
            "resolution": None,
            "is_series": False,
        }
        
        # Try to extract year
        year_match = re.search(r'(19|20)\d{2}', name_without_ext)
        if year_match:
            result["year"] = int(year_match.group())
            
        # Try SxxExx pattern
        sexe_match = re.search(r'[Ss](\d{1,2})[Ee](\d{1,2})', name_without_ext)
        if sexe_match:
            result["is_series"] = True
            result["season"] = int(sexe_match.group(1))
            result["episode"] = int(sexe_match.group(2))
            
        # Try xxXxx pattern (1x01)
        xex_match = re.search(r'(\d{1,2})x(\d{1,2})', name_without_ext)
        if xex_match and not sexe_match:
            result["is_series"] = True
            result["season"] = int(xex_match.group(1))
            result["episode"] = int(xex_match.group(2))
            
        # Try to extract resolution
        res_match = re.search(r'(2160|1080|720|480)[pi]', name_without_ext, re.IGNORECASE)
        if res_match:
            result["resolution"] = res_match.group(1) + "p"
            
        # Clean up title
        title = name_without_ext
        title = re.sub(r'\.(19|20)\d{2}.*$', '', title)  # Remove year and after
        title = re.sub(r'\.[Ss]\d{1,2}[Ee]\d{1,2}.*$', '', title)  # Remove SxxExx
        title = re.sub(r'\.\d{1,2}x\d{1,2}.*$', '', title)  # Remove 1x01
        title = re.sub(r'\.(2160|1080|720|480)[pi].*$', '', title, flags=re.IGNORECASE)
        title = title.replace('.', ' ').replace('_', ' ')
        result["title"] = title.strip()
        
        return result
    
    async def _create_media_item(
        self,
        library_id: str,
        library_type: str,
        file_info: Dict[str, Any],
        parsed: Dict[str, Any],
    ) -> Optional[MediaItem]:
        """
        Create a media item and video file from scanned data.
        
        Args:
            library_id: Library ID
            library_type: Type of library
            file_info: File information
            parsed: Parsed filename metadata
            
        Returns:
            Created MediaItem or None
        """
        from app.media.probe import probe_video_file
        
        # Probe the video file for technical details
        probe_result = await probe_video_file(file_info["path"])
        
        # Determine media type
        if library_type in ["movies"] and not parsed["is_series"]:
            media_type = MediaType.MOVIE
        elif library_type in ["series", "anime"] and parsed["is_series"]:
            # For series, we need to create Series -> Season -> Episode structure
            media_type = MediaType.EPISODE
        else:
            media_type = MediaType.MOVIE  # Default to movie
        
        # Create base media item
        media_item = MediaItem(
            library_id=library_id,
            type=media_type,
            title=parsed["title"],
            year=parsed["year"],
        )
        
        self.db.add(media_item)
        await self.db.flush()  # Get the ID
        
        # Create video file record
        video_file = VideoFile(
            media_id=media_item.id,
            path=file_info["path"],
            filename=file_info["filename"],
            size=file_info["size"],
            duration=probe_result.get("duration"),
            container=probe_result.get("container"),
            video_codec=probe_result.get("video_codec"),
            audio_codec=probe_result.get("audio_codec"),
            resolution=probe_result.get("resolution"),
            width=probe_result.get("width"),
            height=probe_result.get("height"),
            bitrate=probe_result.get("bitrate"),
            framerate=probe_result.get("framerate"),
            hdr=probe_result.get("hdr", False),
            audio_tracks=probe_result.get("audio_tracks", []),
            subtitle_tracks=probe_result.get("subtitle_tracks", []),
        )
        
        self.db.add(video_file)
        await self.db.commit()
        await self.db.refresh(media_item)
        
        logger.info(f"Created media item: {media_item.title} ({media_item.type})")
        
        return media_item


async def run_scan(db: AsyncSession, job_id: str) -> None:
    """
    Run a media scan job.
    
    This function is called by the background task processor.
    
    Args:
        db: Database session
        job_id: Scan job ID to process
    """
    scanner = MediaScanner(db)
    scanner._current_job_id = job_id
    await scanner.scan_library(job_id)


async def scan_all_libraries(db: AsyncSession) -> List[str]:
    """
    Trigger scans for all enabled libraries.
    
    Args:
        db: Database session
        
    Returns:
        List of created scan job IDs
    """
    from app.services.library import create_scan_job, get_libraries
    
    job_ids = []
    libraries = await get_libraries(db, include_disabled=False)
    
    for library in libraries:
        job = await create_scan_job(db, library.id, "full")
        if job:
            job_ids.append(job.id)
            # Schedule scan
            asyncio.create_task(run_scan(db, job.id))
    
    return job_ids
