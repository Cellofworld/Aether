"""
Configuration management for Aether Media Server.

Loads settings from environment variables with sensible defaults.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Aether Media"
    APP_ENV: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://aether:aether@localhost:5432/aether_media",
        description="PostgreSQL connection URL",
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Security
    JWT_SECRET: str = Field(
        default="change-this-to-a-secure-random-secret-in-production",
        description="Secret key for JWT token encoding",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Cookie settings
    COOKIE_SECURE: bool = False
    COOKIE_SAME_SITE: str = "lax"

    # Media Storage
    MEDIA_ROOT: str = "/media"
    TRANSCODE_ROOT: str = "/transcode"
    IMAGE_CACHE_ROOT: str = "/cache/images"
    MAX_UPLOAD_SIZE: int = 1073741824  # 1GB

    # Transcoding
    TRANSCODING_ENABLED: bool = True
    HARDWARE_ACCELERATION: str = "none"  # none, nvidia, vaapi, qsv
    TRANSCODE_CRF: int = 23
    TRANSCODE_PRESET: str = "medium"
    HLS_SEGMENT_DURATION: int = 4
    HLS_PLAYLIST_TYPE: str = "vod"
    AUDIO_BITRATE: int = 192
    VIDEO_BITRATE_CAP: int = 0  # 0 = unlimited
    MAX_TRANSCODE_RESOLUTION: str = "0x0"  # 0x0 = original

    # Metadata Providers
    TMDB_API_KEY: Optional[str] = None
    TMDB_LANGUAGE: str = "en-US"
    TVDB_API_KEY: Optional[str] = None
    FANART_API_KEY: Optional[str] = None

    # Scanner
    SCAN_ON_STARTUP: bool = True
    SCAN_INTERVAL: int = 60  # minutes, 0 = disabled
    FILESYSTEM_WATCHER: bool = False
    MIN_FILE_SIZE: int = 10485760  # 10MB
    VIDEO_EXTENSIONS: str = "mkv,mp4,avi,mov,webm,m4v,wmv,flv"

    # Image Cache
    IMAGE_CACHE_TTL_DAYS: int = 30

    # Network
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    TRUSTED_PROXIES: str = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN: int = 10  # per minute
    RATE_LIMIT_API: int = 100  # per minute per user

    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def video_extensions_list(self) -> List[str]:
        """Get list of supported video extensions."""
        return [ext.strip().lower() for ext in self.VIDEO_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Get list of allowed CORS origins."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def trusted_proxies_list(self) -> List[str]:
        """Get list of trusted proxy networks."""
        return [proxy.strip() for proxy in self.TRUSTED_PROXIES.split(",")]

    @property
    def max_transcode_resolution_tuple(self) -> tuple[int, int]:
        """Get max transcode resolution as tuple."""
        parts = self.MAX_TRANSCODE_RESOLUTION.split("x")
        return (int(parts[0]), int(parts[1]))


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures we only load settings once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
