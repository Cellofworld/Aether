import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base, get_db_session
from app.api import auth, libraries, media, search, playback, admin, users
from app.services.scanner import MediaScannerService
from app.core.logging_config import setup_logging

# Настройка логгирования
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Starting up Aether Media Server...")
    
    # Создание таблиц БД (для dev, в prod лучше использовать alembic upgrade head)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created/verified.")
    
    # Запуск начального сканирования если включено
    if settings.SCAN_ON_STARTUP:
        logger.info("Starting initial library scan...")
        try:
            # Запускаем в фоне, чтобы не блокировать старт
            import asyncio
            from app.services.scanner import ScanJob
            job = ScanJob(job_type="full_scan")
            asyncio.create_task(job.run())
        except Exception as e:
            logger.error(f"Failed to start initial scan: {e}")

    yield
    
    # Shutdown
    logger.info("Shutting down Aether Media Server...")
    # Здесь можно добавить очистку временных файлов транскодинга

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Self-hosted media server with TV-friendly UI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS настройки (важно для frontend на отдельном порту/домене)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(libraries.router, prefix="/api/libraries", tags=["Libraries"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(playback.router, prefix="/api/playback", tags=["Playback"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Статические файлы (постеры, бэкдропы)
# В продакшене это лучше делать через Nginx, но для простоты оставим здесь
app.mount("/images", StaticFiles(directory=settings.IMAGE_CACHE_DIR), name="images")

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
