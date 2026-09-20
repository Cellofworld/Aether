"""Media scanner service."""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.config import settings
from app.models.library import Library, LibraryPath
from app.models.media import MediaItem, Movie, Series, Season, Episode, VideoFile, AudioTrack, SubtitleTrack
from app.models.metadata import Genre, Person, MetadataImage
from app.media.parser import parse_filename, find_subtitle_files
from app.media.probe import probe_video_file

logger = logging.getLogger(__name__)

class MediaScanner:
    """Service for scanning media libraries."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.is_running = False
        self.current_library: Optional[Library] = None
        self.progress = {
            "total": 0,
            "current": 0,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "errors": 0,
            "current_file": "",
            "status": "idle"
        }
    
    async def scan_library(self, library_id: int) -> Dict[str, Any]:
        """Scan a specific library."""
        if self.is_running:
            raise RuntimeError("Scanner is already running")
        
        self.is_running = True
        self.progress = {
            "total": 0,
            "current": 0,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "errors": 0,
            "current_file": "",
            "status": "starting"
        }
        
        try:
            # Get library
            result = await self.db.execute(
                select(Library).where(Library.id == library_id)
            )
            library = result.scalar_one_or_none()
            
            if not library:
                raise ValueError(f"Library {library_id} not found")
            
            self.current_library = library
            self.progress["status"] = "scanning"
            
            # Scan all paths for this library
            for lib_path in library.paths:
                await self._scan_path(library, lib_path.path)
            
            # Clean up removed files
            await self._cleanup_removed_files(library)
            
            self.progress["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            self.progress["status"] = "failed"
            raise
        finally:
            self.is_running = False
            self.current_library = None
        
        return self.progress.copy()
    
    async def _scan_path(self, library: Library, path_str: str):
        """Scan a single directory path."""
        path = Path(path_str)
        
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return
        
        logger.info(f"Scanning path: {path}")
        
        # Collect all video files
        video_files = []
        for ext in ['*.mkv', '*.mp4', '*.avi', '*.mov', '*.webm', '*.m4v']:
            video_files.extend(path.rglob(ext))
        
        self.progress["total"] += len(video_files)
        
        for video_path in video_files:
            try:
                self.progress["current_file"] = str(video_path)
                await self._process_file(library, video_path)
                self.progress["current"] += 1
                self.progress["added"] += 1  # Simplified for now
            except Exception as e:
                logger.error(f"Error processing {video_path}: {e}")
                self.progress["errors"] += 1
                self.progress["current"] += 1
            
            # Commit periodically to avoid long transactions
            if self.progress["current"] % 10 == 0:
                await self.db.commit()
    
    async def _process_file(self, library: Library, file_path: Path):
        """Process a single video file."""
        # Parse filename
        parsed = parse_filename(str(file_path), str(file_path))
        
        if parsed["type"] == "unknown":
            logger.debug(f"Skipping unknown file type: {file_path}")
            return
        
        # Probe file for technical details
        try:
            info = await probe_video_file(str(file_path))
        except Exception as e:
            logger.error(f"Failed to probe {file_path}: {e}")
            info = {}
        
        # Find subtitles
        subtitles = find_subtitle_files(file_path)
        
        # Create or update media item
        if parsed["type"] == "movie":
            await self._process_movie(library, file_path, parsed, info, subtitles)
        elif parsed["type"] == "series":
            await self._process_series(library, file_path, parsed, info, subtitles)
    
    async def _process_movie(self, library: Library, file_path: Path, parsed: Dict, info: Dict, subtitles: Dict):
        """Process a movie file."""
        title = parsed["title"]
        year = parsed.get("year")
        
        # Check if movie already exists
        result = await self.db.execute(
            select(Movie).where(
                Movie.library_id == library.id,
                Movie.title == title
            )
        )
        movie = result.scalar_one_or_none()
        
        if not movie:
            # Create new movie
            movie = Movie(
                library_id=library.id,
                title=title,
                year=year,
                status="pending_metadata"  # Needs metadata fetch
            )
            self.db.add(movie)
            await self.db.flush()
        
        # Create/Update video file
        await self._update_video_file(movie, file_path, info, subtitles)
    
    async def _process_series(self, library: Library, file_path: Path, parsed: Dict, info: Dict, subtitles: Dict):
        """Process a series episode file."""
        title = parsed["title"]
        season_num = parsed.get("season", 1)
        episode_num = parsed.get("episode", 1)
        
        # Find or create series
        result = await self.db.execute(
            select(Series).where(
                Series.library_id == library.id,
                Series.title == title
            )
        )
        series = result.scalar_one_or_none()
        
        if not series:
            series = Series(
                library_id=library.id,
                title=title,
                status="pending_metadata"
            )
            self.db.add(series)
            await self.db.flush()
        
        # Find or create season
        result = await self.db.execute(
            select(Season).where(
                Season.series_id == series.id,
                Season.season_number == season_num
            )
        )
        season = result.scalar_one_or_none()
        
        if not season:
            season = Season(
                series_id=series.id,
                season_number=season_num
            )
            self.db.add(season)
            await self.db.flush()
        
        # Find or create episode
        result = await self.db.execute(
            select(Episode).where(
                Episode.season_id == season.id,
                Episode.episode_number == episode_num
            )
        )
        episode = result.scalar_one_or_none()
        
        if not episode:
            episode = Episode(
                season_id=season.id,
                episode_number=episode_num,
                title=parsed.get("original_name", f"Episode {episode_num}")
            )
            self.db.add(episode)
            await self.db.flush()
        
        # Update video file
        await self._update_video_file(episode, file_path, info, subtitles)
    
    async def _update_video_file(self, parent: Any, file_path: Path, info: Dict, subtitles: Dict):
        """Create or update video file record."""
        # Check if file already exists
        result = await self.db.execute(
            select(VideoFile).where(VideoFile.path == str(file_path))
        )
        video_file = result.scalar_one_or_none()
        
        if not video_file:
            video_file = VideoFile(
                media_id=parent.id,
                path=str(file_path),
                size=file_path.stat().st_size if file_path.exists() else 0,
                duration=info.get("duration", 0),
                width=info.get("width", 0),
                height=info.get("height", 0),
                codec=info.get("codec", ""),
                bitrate=info.get("bitrate", 0),
                framerate=info.get("framerate", 0.0),
                container=file_path.suffix.lower().replace(".", "")
            )
            self.db.add(video_file)
            await self.db.flush()
            
            # Create audio tracks
            for i, audio in enumerate(info.get("audio_streams", [])):
                track = AudioTrack(
                    video_file_id=video_file.id,
                    index=i,
                    codec=audio.get("codec", ""),
                    language=audio.get("language", "unk"),
                    channels=audio.get("channels", 0),
                    bitrate=audio.get("bitrate", 0),
                    title=audio.get("title", "")
                )
                self.db.add(track)
            
            # Create subtitle tracks (external)
            for lang, sub_path in subtitles.items():
                track = SubtitleTrack(
                    video_file_id=video_file.id,
                    language=lang,
                    path=str(sub_path),
                    is_external=True
                )
                self.db.add(track)
    
    async def _cleanup_removed_files(self, library: Library):
        """Remove database entries for files that no longer exist."""
        # Get all video files for this library
        result = await self.db.execute(
            select(VideoFile)
            .join(MediaItem)
            .where(MediaItem.library_id == library.id)
        )
        video_files = result.scalars().all()
        
        for vf in video_files:
            if not Path(vf.path).exists():
                logger.info(f"Removing missing file: {vf.path}")
                await self.db.delete(vf)
                self.progress["removed"] += 1
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current scan progress."""
        return self.progress.copy()


# Global scanner instance (will be managed by dependency injection in real app)
_scanner_instance: Optional[MediaScanner] = None

def get_scanner(db: AsyncSession) -> MediaScanner:
    """Get or create scanner instance."""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = MediaScanner(db)
    return _scanner_instance
