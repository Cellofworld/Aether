"""Core configuration and settings."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Aether Media Server"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aether"
    
    # Security
    JWT_SECRET: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Media
    MEDIA_ROOT: str = "/media"
    TRANSCODE_ROOT: str = "/transcode"
    
    # Transcoding
    TRANSCODING_ENABLED: bool = True
    HARDWARE_ACCELERATION: str = "none"  # none, nvidia, vaapi, qsv
    TRANSCODE_BITRATE: int = 4000000  # 4 Mbps
    TRANSCODE_AUDIO_BITRATE: int = 192000  # 192 kbps
    
    # TMDB
    TMDB_API_KEY: Optional[str] = None
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE: str = "https://image.tmdb.org/t/p"
    
    # Scanner
    SCAN_INTERVAL: int = 1800  # 30 minutes in seconds
    SCAN_ON_STARTUP: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
