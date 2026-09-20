"""Сервис для получения метаданных из внешних источников."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class MetadataProvider:
    """Базовый класс для провайдеров метаданных."""

    async def search(self, query: str, media_type: str = "movie") -> List[Dict[str, Any]]:
        """Поиск по названию."""
        raise NotImplementedError()

    async def get_details(self, external_id: str, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Получить подробную информацию."""
        raise NotImplementedError()

    async def get_image(self, image_path: str, size: str = "original") -> Optional[bytes]:
        """Загрузить изображение."""
        raise NotImplementedError()


class TMDBProvider(MetadataProvider):
    """Провайдер метаданных The Movie Database."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base = settings.TMDB_IMAGE_BASE
        
        if not self.api_key:
            logger.warning("TMDB API key not configured. Metadata features will be limited.")

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Выполнить HTTP запрос к API TMDB."""
        if not self.api_key:
            return None

        url = f"{self.base_url}/{endpoint}"
        request_params = {"api_key": self.api_key}
        if params:
            request_params.update(params)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=request_params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"TMDB API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching from TMDB: {e}")
            return None

    async def search(self, query: str, media_type: str = "multi") -> List[Dict[str, Any]]:
        """
        Поиск по названию.
        
        Args:
            query: Поисковый запрос
            media_type: Тип медиа (movie, tv, multi)
            
        Returns:
            Список результатов поиска
        """
        if not self.api_key:
            return []

        result = await self._make_request(
            f"/search/{media_type}",
            {"query": query, "include_adult": False}
        )

        if not result or "results" not in result:
            return []

        return result["results"]

    async def get_movie_details(self, tmdb_id: str) -> Optional[Dict[str, Any]]:
        """Получить детали фильма."""
        result = await self._make_request(f"/movie/{tmdb_id}", {"append_to_response": "credits,videos"})
        if not result:
            return None

        return self._normalize_movie(result)

    async def get_tv_details(self, tmdb_id: str) -> Optional[Dict[str, Any]]:
        """Получить детали сериала."""
        result = await self._make_request(f"/tv/{tmdb_id}", {"append_to_response": "credits,videos,seasons"})
        if not result:
            return None

        return self._normalize_tv_show(result)

    async def get_season_details(self, tv_id: str, season_number: int) -> Optional[Dict[str, Any]]:
        """Получить детали сезона."""
        result = await self._make_request(f"/tv/{tv_id}/season/{season_number}")
        if not result:
            return None

        return self._normalize_season(result)

    async def get_episode_details(self, tv_id: str, season_number: int, episode_number: int) -> Optional[Dict[str, Any]]:
        """Получить детали эпизода."""
        result = await self._make_request(f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}")
        if not result:
            return None

        return self._normalize_episode(result)

    async def get_image(self, image_path: str, size: str = "w500") -> Optional[bytes]:
        """
        Загрузить изображение.
        
        Args:
            image_path: Путь к изображению от API
            size: Размер (w92, w154, w185, w342, w500, w780, original)
        """
        if not image_path or not self.api_key:
            return None

        url = f"{self.image_base}/{size}{image_path}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")
            return None

    def _normalize_movie(self, data: Dict) -> Dict[str, Any]:
        """Нормализовать данные фильма."""
        return {
            "id": str(data.get("id")),
            "title": data.get("title"),
            "original_title": data.get("original_title"),
            "overview": data.get("overview"),
            "release_date": data.get("release_date"),
            "year": int(data.get("release_date", "0000")[:4]) if data.get("release_date") else None,
            "runtime": data.get("runtime"),
            "rating": data.get("vote_average"),
            "votes": data.get("vote_count"),
            "genres": [{"id": g.get("id"), "name": g.get("name")} for g in data.get("genres", [])],
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "cast": [
                {
                    "name": c.get("name"),
                    "character": c.get("character"),
                    "profile_path": c.get("profile_path")
                }
                for c in data.get("credits", {}).get("cast", [])[:10]
            ],
            "directors": [
                {
                    "name": c.get("name"),
                    "profile_path": c.get("profile_path")
                }
                for c in data.get("credits", {}).get("crew", [])
                if c.get("job") == "Director"
            ],
            "trailer_key": self._extract_trailer_key(data.get("videos", {})),
            "external_ids": {
                "tmdb": data.get("id"),
                "imdb": data.get("imdb_id"),
            }
        }

    def _normalize_tv_show(self, data: Dict) -> Dict[str, Any]:
        """Нормализовать данные сериала."""
        return {
            "id": str(data.get("id")),
            "title": data.get("name"),
            "original_title": data.get("original_name"),
            "overview": data.get("overview"),
            "first_air_date": data.get("first_air_date"),
            "year": int(data.get("first_air_date", "0000")[:4]) if data.get("first_air_date") else None,
            "runtime": data.get("episode_run_time", [None])[0] if data.get("episode_run_time") else None,
            "rating": data.get("vote_average"),
            "votes": data.get("vote_count"),
            "genres": [{"id": g.get("id"), "name": g.get("name")} for g in data.get("genres", [])],
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "number_of_seasons": data.get("number_of_seasons"),
            "number_of_episodes": data.get("number_of_episodes"),
            "cast": [
                {
                    "name": c.get("name"),
                    "character": c.get("character"),
                    "profile_path": c.get("profile_path")
                }
                for c in data.get("credits", {}).get("cast", [])[:10]
            ],
            "creators": [
                {
                    "name": c.get("name"),
                    "profile_path": c.get("profile_path")
                }
                for c in data.get("created_by", [])
            ],
            "trailer_key": self._extract_trailer_key(data.get("videos", {})),
            "external_ids": {
                "tmdb": data.get("id"),
                "tvdb": data.get("external_ids", {}).get("tvdb_id"),
                "imdb": data.get("external_ids", {}).get("imdb_id"),
            },
            "seasons": [
                {
                    "season_number": s.get("season_number"),
                    "name": s.get("name"),
                    "overview": s.get("overview"),
                    "poster_path": s.get("poster_path"),
                    "episode_count": s.get("episode_count"),
                    "air_date": s.get("air_date")
                }
                for s in data.get("seasons", [])
            ]
        }

    def _normalize_season(self, data: Dict) -> Dict[str, Any]:
        """Нормализовать данные сезона."""
        return {
            "season_number": data.get("season_number"),
            "name": data.get("name"),
            "overview": data.get("overview"),
            "poster_path": data.get("poster_path"),
            "air_date": data.get("air_date"),
            "episodes": [
                self._normalize_episode(ep) for ep in data.get("episodes", [])
            ]
        }

    def _normalize_episode(self, data: Dict) -> Dict[str, Any]:
        """Нормализовать данные эпизода."""
        return {
            "episode_number": data.get("episode_number"),
            "name": data.get("name"),
            "overview": data.get("overview"),
            "air_date": data.get("air_date"),
            "runtime": data.get("runtime"),
            "still_path": data.get("still_path"),
            "rating": data.get("vote_average"),
        }

    @staticmethod
    def _extract_trailer_key(videos: Dict) -> Optional[str]:
        """Извлечь ключ трейлера YouTube."""
        if not videos or "results" not in videos:
            return None

        for video in videos.get("results", []):
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return video.get("key")

        return None


class MetadataService:
    """Сервис для управления метаданными."""

    def __init__(self):
        self.provider = TMDBProvider()

    async def search(self, query: str, media_type: str = "multi") -> List[Dict[str, Any]]:
        """Поиск метаданных."""
        return await self.provider.search(query, media_type)

    async def get_movie_metadata(self, tmdb_id: str) -> Optional[Dict[str, Any]]:
        """Получить метаданные фильма."""
        return await self.provider.get_movie_details(tmdb_id)

    async def get_tv_metadata(self, tmdb_id: str) -> Optional[Dict[str, Any]]:
        """Получить метаданные сериала."""
        return await self.provider.get_tv_details(tmdb_id)

    async def download_image(self, image_path: str, size: str = "w500") -> Optional[bytes]:
        """Загрузить изображение."""
        return await self.provider.get_image(image_path, size)
