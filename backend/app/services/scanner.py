"""Сервис сканирования медиабиблиотек."""

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


class ScanJob:
    """Фоновая задача сканирования."""

    def __init__(self, job_type: str = "full_scan", library_id: Optional[int] = None):
        self.job_type = job_type
        self.library_id = library_id
        self.status = "pending"
        self.progress = 0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Dict[str, Any] = {}

    async def run(self):
        """Запуск задачи сканирования."""
        from app.core.database import async_session_maker
        
        self.status = "running"
        self.started_at = datetime.utcnow()
        
        async with async_session_maker() as session:
            scanner = MediaScannerService(session)
            
            if self.job_type == "full_scan":
                # Сканировать все библиотеки
                result = await scanner.scan_all_libraries()
            elif self.library_id:
                # Сканировать конкретную библиотеку
                result = await scanner.scan_library(self.library_id)
            else:
                result = {"error": "No library specified"}
            
            self.result = result
            self.status = "completed"
            self.completed_at = datetime.utcnow()
            
        return self.result


class MediaScannerService:
    """Сервис для сканирования медиатек."""

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

    async def scan_all_libraries(self) -> Dict[str, Any]:
        """Сканировать все библиотеки."""
        result = await self.db.execute(select(Library))
        libraries = result.scalars().all()
        
        total_result = {
            "libraries_scanned": len(libraries),
            "results": []
        }
        
        for library in libraries:
            try:
                lib_result = await self.scan_library(library.id)
                total_result["results"].append({
                    "library_id": library.id,
                    "library_name": library.name,
                    "result": lib_result
                })
            except Exception as e:
                logger.error(f"Failed to scan library {library.name}: {e}")
                total_result["results"].append({
                    "library_id": library.id,
                    "library_name": library.name,
                    "error": str(e)
                })
        
        return total_result

    async def scan_library(self, library_id: int) -> Dict[str, Any]:
        """Сканировать конкретную библиотеку."""
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
            # Получить библиотеку
            result = await self.db.execute(
                select(Library).where(Library.id == library_id)
            )
            library = result.scalar_one_or_none()

            if not library:
                raise ValueError(f"Library {library_id} not found")

            self.current_library = library
            self.progress["status"] = "scanning"

            # Сканировать все пути для этой библиотеки
            for lib_path in library.paths:
                await self._scan_path(library, lib_path.path)

            # Очистить удаленные файлы
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
        """Сканировать один каталог."""
        path = Path(path_str)

        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return

        logger.info(f"Scanning path: {path}")

        # Собрать все видеофайлы
        video_files = []
        for ext in ['*.mkv', '*.mp4', '*.avi', '*.mov', '*.webm', '*.m4v']:
            video_files.extend(path.rglob(ext))

        self.progress["total"] += len(video_files)

        for video_path in video_files:
            try:
                self.progress["current_file"] = str(video_path)
                await self._process_file(library, video_path)
                self.progress["current"] += 1
            except Exception as e:
                logger.error(f"Error processing {video_path}: {e}")
                self.progress["errors"] += 1

    async def _process_file(self, library: Library, file_path: Path):
        """Обработать один видеофайл."""
        # Распарсить имя файла
        parsed = parse_filename(file_path.name, file_path.parent.name)
        
        if not parsed:
            logger.warning(f"Could not parse filename: {file_path.name}")
            self.progress["errors"] += 1
            return

        # Получить метаданные из файла
        file_info = await probe_video_file(str(file_path))
        
        if not file_info:
            logger.warning(f"Could not probe file: {file_path}")
            self.progress["errors"] += 1
            return

        # Создать или обновить MediaItem
        await self._create_or_update_media_item(library, parsed, file_path, file_info)

    async def _create_or_update_media_item(self, library: Library, parsed: dict, file_path: Path, file_info: dict):
        """Создать или обновить элемент медиа."""
        # Логика создания/обновления зависит от типа контента
        media_type = parsed.get("type", "movie")
        
        if media_type == "movie":
            await self._process_movie(library, parsed, file_path, file_info)
        elif media_type == "series":
            await self._process_series(library, parsed, file_path, file_info)
        else:
            logger.warning(f"Unknown media type: {media_type}")

    async def _process_movie(self, library: Library, parsed: dict, file_path: Path, file_info: dict):
        """Обработать фильм."""
        # Проверить существует ли уже
        result = await self.db.execute(
            select(Movie).where(
                Movie.title == parsed.get("title"),
                Movie.year == parsed.get("year")
            )
        )
        movie = result.scalar_one_or_none()

        if not movie:
            # Создать новый фильм
            movie = Movie(
                title=parsed.get("title", "Unknown"),
                original_title=parsed.get("original_title"),
                year=parsed.get("year"),
                library_id=library.id
            )
            self.db.add(movie)
            await self.db.flush()
            self.progress["added"] += 1
        else:
            self.progress["updated"] += 1

        # Создать VideoFile
        video_file = VideoFile(
            media_item_id=movie.id,
            file_path=str(file_path),
            file_size=file_info.get("size", 0),
            duration=file_info.get("duration", 0),
            container=file_info.get("format", {}).get("format_name", ""),
            video_codec=file_info.get("video_codec", ""),
            audio_codec=file_info.get("audio_codec", ""),
            width=file_info.get("width", 0),
            height=file_info.get("height", 0),
            bitrate=file_info.get("bitrate", 0),
            framerate=file_info.get("framerate", 0),
            hdr=file_info.get("hdr", False)
        )
        self.db.add(video_file)

        # Добавить аудиодорожки
        for audio in file_info.get("audio_streams", []):
            audio_track = AudioTrack(
                video_file_id=video_file.id,
                index=audio.get("index", 0),
                language=audio.get("language", "und"),
                codec=audio.get("codec", ""),
                channels=audio.get("channels", 0),
                title=audio.get("title")
            )
            self.db.add(audio_track)

        # Добавить субтитры
        subtitle_files = find_subtitle_files(file_path)
        for sub_path in subtitle_files:
            sub_parsed = parse_filename(sub_path.name)
            subtitle_track = SubtitleTrack(
                video_file_id=video_file.id,
                file_path=str(sub_path),
                language=sub_parsed.get("language", "und") if sub_parsed else "und",
                is_embedded=False
            )
            self.db.add(subtitle_track)

        await self.db.commit()

    async def _process_series(self, library: Library, parsed: dict, file_path: Path, file_info: dict):
        """Обработать сериал."""
        series_title = parsed.get("series_title")
        season_number = parsed.get("season", 1)
        episode_number = parsed.get("episode")

        if not episode_number:
            logger.warning(f"No episode number found: {file_path}")
            self.progress["errors"] += 1
            return

        # Найти или создать сериал
        result = await self.db.execute(
            select(Series).where(
                Series.title == series_title
            )
        )
        series = result.scalar_one_or_none()

        if not series:
            series = Series(
                title=series_title or "Unknown Series",
                library_id=library.id
            )
            self.db.add(series)
            await self.db.flush()
            self.progress["added"] += 1

        # Найти или создать сезон
        result = await self.db.execute(
            select(Season).where(
                Season.series_id == series.id,
                Season.season_number == season_number
            )
        )
        season = result.scalar_one_or_none()

        if not season:
            season = Season(
                series_id=series.id,
                season_number=season_number
            )
            self.db.add(season)
            await self.db.flush()

        # Создать эпизод
        episode = Episode(
            season_id=season.id,
            episode_number=episode_number,
            title=parsed.get("episode_title"),
            library_id=library.id
        )
        self.db.add(episode)
        await self.db.flush()
        self.progress["added"] += 1

        # Создать VideoFile для эпизода
        video_file = VideoFile(
            media_item_id=episode.id,
            file_path=str(file_path),
            file_size=file_info.get("size", 0),
            duration=file_info.get("duration", 0),
            container=file_info.get("format", {}).get("format_name", ""),
            video_codec=file_info.get("video_codec", ""),
            audio_codec=file_info.get("audio_codec", ""),
            width=file_info.get("width", 0),
            height=file_info.get("height", 0),
            bitrate=file_info.get("bitrate", 0),
            framerate=file_info.get("framerate", 0),
            hdr=file_info.get("hdr", False)
        )
        self.db.add(video_file)
        await self.db.commit()

    async def _cleanup_removed_files(self, library: Library):
        """Удалить записи о файлах которые больше не существуют."""
        # Получить все VideoFile для этой библиотеки
        result = await self.db.execute(
            select(VideoFile)
            .join(MediaItem)
            .where(MediaItem.library_id == library.id)
        )
        video_files = result.scalars().all()

        removed_count = 0
        for vf in video_files:
            if not Path(vf.file_path).exists():
                await self.db.delete(vf)
                removed_count += 1

        if removed_count > 0:
            await self.db.commit()
            logger.info(f"Removed {removed_count} non-existent files")

        self.progress["removed"] = removed_count
