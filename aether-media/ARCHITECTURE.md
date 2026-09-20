# Aether Media Server - Architecture & Implementation Plan

## 1. Project Overview

Aether Media Server is a self-hosted media server application designed for home use, inspired by Jellyfin/Plex but built as an independent project with modern architecture.

### Key Features
- Local media library management
- Automatic media scanning and metadata fetching
- Beautiful UI with posters, descriptions, ratings
- In-browser video playback with transcoding support
- Smart TV friendly interface
- Resume playback functionality
- Multi-audio track and subtitle support
- Full-text search and filtering
- User authentication and roles
- Docker-based deployment

---

## 2. Technology Stack

### Backend
- **Python 3.12+** - Main programming language
- **FastAPI** - Web framework for API
- **SQLAlchemy 2.0** - ORM for database operations
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Redis** - Caching and task queue
- **FFmpeg/FFprobe** - Media processing and transcoding
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **httpx** - Async HTTP client for metadata APIs
- **watchfiles** - Filesystem watching

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **TanStack Query** - Server state management
- **React Router** - Client-side routing
- **Zustand** - Client state management
- **shadcn/ui** - Component library
- **Video.js / Hls.js** - Video playback

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **PostgreSQL** - Database
- **Redis** - Cache and queues

---

## 3. Directory Structure

```
aether-media/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── libraries.py
│   │   │   │   ├── media.py
│   │   │   │   ├── movies.py
│   │   │   │   ├── series.py
│   │   │   │   ├── search.py
│   │   │   │   ├── playback.py
│   │   │   │   ├── stream.py
│   │   │   │   ├── admin.py
│   │   │   │   └── users.py
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── db/               # Database setup
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── library.py
│   │   │   ├── media.py
│   │   │   ├── movie.py
│   │   │   ├── series.py
│   │   │   ├── episode.py
│   │   │   ├── watch_progress.py
│   │   │   └── ...
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── library.py
│   │   │   ├── media.py
│   │   │   └── ...
│   │   ├── services/         # Business logic
│   │   │   ├── auth.py
│   │   │   ├── library.py
│   │   │   ├── media.py
│   │   │   ├── metadata.py
│   │   │   ├── scanner.py
│   │   │   ├── streaming.py
│   │   │   └── transcoding.py
│   │   ├── repositories/     # Data access layer
│   │   │   ├── user.py
│   │   │   ├── library.py
│   │   │   └── ...
│   │   ├── workers/          # Background tasks
│   │   │   ├── scanner.py
│   │   │   ├── metadata.py
│   │   │   └── cleanup.py
│   │   ├── media/            # Media processing
│   │   │   ├── parser.py     # Filename parsing
│   │   │   ├── probe.py      # FFprobe wrapper
│   │   │   └── utils.py
│   │   ├── metadata/         # Metadata providers
│   │   │   ├── base.py
│   │   │   ├── tmdb.py
│   │   │   └── tvdb.py
│   │   └── main.py           # Application entry point
│   ├── migrations/           # Alembic migrations
│   ├── tests/                # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   │   ├── ui/           # Base UI components
│   │   │   ├── media/        # Media-related components
│   │   │   ├── layout/       # Layout components
│   │   │   └── player/       # Video player components
│   │   ├── features/         # Feature-specific components
│   │   │   ├── auth/
│   │   │   ├── libraries/
│   │   │   ├── media/
│   │   │   └── admin/
│   │   ├── layouts/          # Page layouts
│   │   │   ├── MainLayout.tsx
│   │   │   ├── TvLayout.tsx
│   │   │   └── AdminLayout.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Library.tsx
│   │   │   ├── Movie.tsx
│   │   │   ├── Series.tsx
│   │   │   ├── Player.tsx
│   │   │   ├── Search.tsx
│   │   │   └── admin/
│   │   ├── hooks/            # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useNavigation.ts
│   │   │   ├── usePlayer.ts
│   │   │   └── useTvNavigation.ts
│   │   ├── services/         # API services
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── media.ts
│   │   │   └── playback.ts
│   │   ├── stores/           # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   ├── playerStore.ts
│   │   │   └── navigationStore.ts
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   ├── manifest.json
│   │   └── icons/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │   Library   │       │  MediaItem  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id          │       │ id          │       │ id          │
│ email       │       │ name        │◄──────│ library_id  │
│ username    │       │ type        │       │ type        │
│ password    │       │ root_path   │       │ title       │
│ role        │       │ created_at  │       │ year        │
│ created_at  │       └─────────────┘       │ metadata    │
│ updated_at  │                              │ created_at  │
└─────────────┘                              └─────────────┘
       │                                            │
       │                                            │
       ▼                                            ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│WatchProgress│       │    Movie    │       │   Series    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id          │       │ id          │       │ id          │
│ user_id     │       │ media_id    │       │ media_id    │
│ media_id    │       │ tmdb_id     │       │ tmdb_id     │
│ position    │       │ runtime     │       │ seasons     │
│ duration    │       │ tagline     │       │ status      │
│ watched     │       └─────────────┘       └─────────────┘
│ updated_at  │                              │
└─────────────┘                                    │
                                                   │
                                                   ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Season    │       │   Episode   │       │  VideoFile  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id          │       │ id          │       │ id          │
│ series_id   │──────►│ season_id   │       │ media_id    │
│ number      │       │ number      │       │ path        │
│ title       │       │ title       │       │ duration    │
└─────────────┘       │ episode_num │       │ size        │
                      │ air_date    │       │ video_codec │
                      └─────────────┘       │ audio_codec │
                                            │ resolution  │
                                            └─────────────┘
```

### Core Tables

#### Users
- `id` (UUID, PK)
- `email` (String, Unique)
- `username` (String, Unique)
- `password_hash` (String)
- `role` (Enum: admin, user)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### Libraries
- `id` (UUID, PK)
- `name` (String)
- `type` (Enum: movies, series, anime, music, photos)
- `root_paths` (JSON - array of paths)
- `scanner_config` (JSON)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### MediaItems
- `id` (UUID, PK)
- `library_id` (FK → Libraries)
- `type` (Enum: movie, series, season, episode)
- `title` (String)
- `original_title` (String)
- `year` (Integer)
- `metadata` (JSON - cached metadata)
- `poster_path` (String)
- `backdrop_path` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### Movies
- `id` (UUID, PK)
- `media_id` (FK → MediaItems)
- `tmdb_id` (Integer)
- `runtime` (Integer)
- `tagline` (String)
- `genres` (JSON)

#### Series
- `id` (UUID, PK)
- `media_id` (FK → MediaItems)
- `tmdb_id` (Integer)
- `status` (String)
- `first_air_date` (Date)
- `last_air_date` (Date)
- `genres` (JSON)

#### Seasons
- `id` (UUID, PK)
- `series_id` (FK → Series)
- `number` (Integer)
- `title` (String)
- `air_date` (Date)

#### Episodes
- `id` (UUID, PK)
- `season_id` (FK → Seasons)
- `number` (Integer)
- `title` (String)
- `overview` (Text)
- `air_date` (Date)
- `runtime` (Integer)

#### VideoFiles
- `id` (UUID, PK)
- `media_id` (FK → MediaItems or Episodes)
- `path` (String)
- `filename` (String)
- `size` (BigInt)
- `duration` (Float)
- `container` (String)
- `video_codec` (String)
- `audio_codec` (String)
- `resolution` (String)
- `bitrate` (Integer)
- `framerate` (Float)
- `hdr` (Boolean)
- `audio_tracks` (JSON)
- `subtitle_tracks` (JSON)

#### WatchProgress
- `id` (UUID, PK)
- `user_id` (FK → Users)
- `media_id` (FK → MediaItems)
- `episode_id` (FK → Episodes, nullable)
- `position_ms` (BigInt)
- `duration_ms` (BigInt)
- `watched` (Boolean)
- `updated_at` (DateTime)

#### Genres
- `id` (UUID, PK)
- `name` (String)
- `tmdb_id` (Integer)

#### Persons
- `id` (UUID, PK)
- `name` (String)
- `tmdb_id` (Integer)
- `profile_path` (String)
- `biography` (Text)
- `birth_date` (Date)
- `death_date` (Date)

#### MediaPerson (Junction Table)
- `media_id` (FK → MediaItems)
- `person_id` (FK → Persons)
- `role` (String: actor, director, writer, etc.)
- `character` (String)
- `order` (Integer)

#### MediaGenre (Junction Table)
- `media_id` (FK → MediaItems)
- `genre_id` (FK → Genres)

#### Watchlist
- `id` (UUID, PK)
- `user_id` (FK → Users)
- `media_id` (FK → MediaItems)
- `created_at` (DateTime)

#### Settings
- `id` (UUID, PK)
- `key` (String, Unique)
- `value` (JSON)
- `updated_at` (DateTime)

#### ScanJobs
- `id` (UUID, PK)
- `library_id` (FK → Libraries)
- `status` (Enum: pending, running, completed, failed)
- `progress` (Integer)
- `items_scanned` (Integer)
- `items_added` (Integer)
- `items_updated` (Integer)
- `items_removed` (Integer)
- `errors` (JSON)
- `started_at` (DateTime)
- `completed_at` (DateTime)

#### PlaybackSessions
- `id` (UUID, PK)
- `user_id` (FK → Users)
- `media_id` (FK → MediaItems)
- `device_info` (JSON)
- `play_method` (Enum: direct_play, remux, transcode)
- `started_at` (DateTime)
- `ended_at` (DateTime)
- `position_ms` (BigInt)

---

## 5. API Architecture

### RESTful API Design

Base URL: `/api/v1`

#### Authentication Endpoints
```
POST   /api/v1/auth/login          - Login user
POST   /api/v1/auth/logout         - Logout user
POST   /api/v1/auth/refresh        - Refresh token
GET    /api/v1/auth/me             - Get current user
```

#### Library Endpoints
```
GET    /api/v1/libraries                    - List all libraries
POST   /api/v1/libraries                    - Create library
GET    /api/v1/libraries/{id}               - Get library details
PUT    /api/v1/libraries/{id}               - Update library
DELETE /api/v1/libraries/{id}               - Delete library
POST   /api/v1/libraries/{id}/scan          - Trigger scan
GET    /api/v1/libraries/{id}/items         - Get library items
GET    /api/v1/libraries/{id}/stats         - Get library statistics
```

#### Media Endpoints
```
GET    /api/v1/movies                       - List movies
GET    /api/v1/movies/{id}                  - Get movie details
GET    /api/v1/series                       - List series
GET    /api/v1/series/{id}                  - Get series details
GET    /api/v1/series/{id}/seasons          - Get seasons
GET    /api/v1/seasons/{id}                 - Get season details
GET    /api/v1/seasons/{id}/episodes        - Get episodes
GET    /api/v1/episodes/{id}                - Get episode details
GET    /api/v1/media/{id}/video             - Get video file info
```

#### Playback Endpoints
```
POST   /api/v1/playback/progress            - Update playback progress
GET    /api/v1/playback/continue            - Get continue watching
POST   /api/v1/playback/session             - Start playback session
DELETE /api/v1/playback/session/{id}        - End playback session
```

#### Streaming Endpoints
```
GET    /api/v1/stream/{id}                  - Direct play stream
GET    /api/v1/stream/{id}/master.m3u8      - HLS master playlist
GET    /api/v1/stream/{id}/{quality}/index.m3u8 - HLS quality playlist
GET    /api/v1/stream/{id}/{segment}        - HLS segment
GET    /api/v1/stream/{id}/subtitles/{lang} - Subtitle file
```

#### Search Endpoints
```
GET    /api/v1/search                       - Global search
GET    /api/v1/search/suggestions           - Search suggestions
```

#### User Endpoints
```
GET    /api/v1/users                        - List users (admin)
POST   /api/v1/users                        - Create user (admin)
GET    /api/v1/users/{id}                   - Get user details
PUT    /api/v1/users/{id}                   - Update user
DELETE /api/v1/users/{id}                   - Delete user (admin)
GET    /api/v1/users/{id}/watchlist         - Get user's watchlist
POST   /api/v1/users/{id}/watchlist         - Add to watchlist
DELETE /api/v1/users/{id}/watchlist/{media} - Remove from watchlist
```

#### Admin Endpoints
```
GET    /api/v1/admin/dashboard              - Dashboard stats
GET    /api/v1/admin/jobs                   - List background jobs
GET    /api/v1/admin/jobs/{id}              - Get job details
POST   /api/v1/admin/jobs/{id}/cancel       - Cancel job
GET    /api/v1/admin/logs                   - Get system logs
GET    /api/v1/admin/settings               - Get settings
PUT    /api/v1/admin/settings               - Update settings
POST   /api/v1/admin/metadata/refresh       - Refresh metadata
```

### WebSocket Events

```
/ws/events

Events:
- scan:progress      - Scanner progress updates
- scan:complete      - Scan completed
- scan:error         - Scan error
- playback:session   - Playback session events
- system:notification - System notifications
```

---

## 6. Docker Architecture

### Services

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: aether
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: aether_media
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aether"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ${MEDIA_ROOT}:/media
      - ${TRANSCODE_ROOT}:/transcode
      - ${IMAGE_CACHE_ROOT}:/cache/images
    environment:
      DATABASE_URL: postgresql://aether:${POSTGRES_PASSWORD}@postgres:5432/aether_media
      REDIS_URL: redis://redis:6379/0
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Background Worker
  worker:
    build: ./backend
    command: python -m app.workers.main
    depends_on:
      - backend
      - redis
    volumes:
      - ${MEDIA_ROOT}:/media
      - ${TRANSCODE_ROOT}:/transcode
    environment:
      DATABASE_URL: postgresql://aether:${POSTGRES_PASSWORD}@postgres:5432/aether_media
      REDIS_URL: redis://redis:6379/0
    env_file:
      - .env

  # Frontend
  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      VITE_API_URL: /api/v1
      VITE_WS_URL: /ws

  # Nginx Reverse Proxy
  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"  # Optional HTTPS
    depends_on:
      - frontend
      - backend
    volumes:
      - ${MEDIA_ROOT}:/media:ro
      - ${TRANSCODE_ROOT}:/transcode:ro
    env_file:
      - .env

volumes:
  postgres_data:
  redis_data:
```

---

## 7. Media Scanner Pipeline

```
┌─────────────────┐
│  Filesystem     │
│  Watcher/Scan   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Discovery │
│  (Recursive)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filename       │
│  Parser         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Media Type     │
│  Detection      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FFprobe        │
│  Analysis       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata       │
│  Matching       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata       │
│  Provider       │
│  (TMDB/TVDB)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Database       │
│  Storage        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Image          │
│  Download       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Library        │
│  Indexing       │
└─────────────────┘
```

### Filename Parsing Patterns

#### Movies
- `Movie Name (2024).mkv`
- `Movie.Name.2024.1080p.BluRay.x264.mkv`
- `Movie Name (2024) [2160p] [HDR].mkv`

#### Series
- `Show.Name.S01E01.mkv`
- `Show.Name.1x01.Episode.Title.mkv`
- `Show.Name.Season.01.Episode.01.mkv`

#### Anime
- `[Group] Anime Name - 01 [1080p].mkv`
- `Anime Name Episode 01.mkv`
- `Anime Name - 01 (BD 1080p).mkv`

---

## 8. Transcoding Strategy

### Play Methods

1. **Direct Play**
   - Browser/Device supports codec and container
   - No processing required
   - Best quality and performance

2. **Direct Stream (Remux)**
   - Codec supported, container not supported
   - Repackage without re-encoding
   - Fast, minimal quality loss

3. **Transcoding**
   - Codec not supported
   - Resolution/bandwidth adaptation needed
   - CPU/GPU intensive

### HLS Transcoding Pipeline

```
FFmpeg Command Structure:

ffmpeg -i input.mkv \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -c:a aac \
  -b:a 192k \
  -f hls \
  -hls_time 4 \
  -hls_playlist_type vod \
  -hls_segment_filename '/transcode/{session_id}/segment_%03d.ts' \
  '/transcode/{session_id}/playlist.m3u8'
```

### Hardware Acceleration Options

- **NVIDIA NVENC**: `-c:v h264_nvenc` or `-c:v hevc_nvenc`
- **Intel Quick Sync**: `-c:v h264_qsv` or `-c:v hevc_qsv`
- **VAAPI**: `-c:v h264_vaapi` or `-c:v hevc_vaapi`

---

## 9. Frontend Architecture

### Component Hierarchy

```
App
├── Router
│   ├── Public Routes
│   │   └── Login
│   └── Protected Routes
│       ├── MainLayout
│       │   ├── Header
│       │   ├── Sidebar
│       │   └── Pages
│       │       ├── Home
│       │       │   ├── Hero Section
│       │       │   ├── Continue Watching
│       │       │   ├── Recently Added
│       │       │   └── Library Shelves
│       │       ├── Library
│       │       │   ├── Filter Bar
│       │       │   └── Media Grid
│       │       ├── Movie Detail
│       │       ├── Series Detail
│       │       │   └── Season/Episode List
│       │       ├── Player
│       │       │   ├── Video Component
│       │       │   ├── Controls
│       │       │   └── Subtitle Overlay
│       │       └── Search
│       └── AdminLayout
│           └── Admin Pages
└── Modals
```

### TV Navigation

- Arrow keys for navigation
- Enter/OK for selection
- Back/Escape for back navigation
- Space for play/pause
- Left/Right for seek
- Up/Down for volume
- Focus states clearly visible
- Large touch targets

---

## 10. Security Considerations

1. **Authentication**
   - JWT tokens with refresh mechanism
   - Secure password hashing (bcrypt)
   - Rate limiting on login

2. **Authorization**
   - Role-based access control
   - Resource-level permissions

3. **Input Validation**
   - Pydantic schemas for all inputs
   - Path traversal protection
   - SQL injection prevention (ORM)

4. **Media Security**
   - Validate media paths are within allowed roots
   - Sanitize FFmpeg arguments
   - Isolate transcoding processes

5. **Network Security**
   - CORS configuration
   - CSRF protection
   - Secure headers via Nginx

---

## 11. Performance Optimizations

1. **Database**
   - Proper indexing on frequently queried columns
   - Connection pooling
   - Query optimization

2. **Caching**
   - Redis for metadata caching
   - Image caching with TTL
   - API response caching

3. **Frontend**
   - Lazy loading of images
   - Virtual scrolling for large lists
   - Code splitting
   - TanStack Query for server state

4. **Streaming**
   - HTTP Range requests for direct play
   - Efficient HLS segment generation
   - Cleanup of old transcode sessions

---

## 12. Testing Strategy

### Backend Tests
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database tests with fixtures
- Media scanner tests with sample files

### Frontend Tests
- Component unit tests
- Integration tests for pages
- E2E tests with Playwright

---

## 13. Monitoring & Logging

1. **Structured Logging**
   - JSON format logs
   - Correlation IDs for requests
   - Log levels (DEBUG, INFO, WARNING, ERROR)

2. **Health Checks**
   - Database connectivity
   - Redis connectivity
   - Media storage accessibility

3. **Metrics** (Future)
   - Request latency
   - Transcoding performance
   - Storage usage

---

## 14. Implementation Phases

### Phase 1: Foundation
- Project structure
- Database models
- Authentication system
- Basic API setup

### Phase 2: Media Library
- Library CRUD
- Media scanner
- FFprobe integration
- Metadata providers

### Phase 3: Frontend Core
- React app setup
- Authentication UI
- Home page
- Library browsing

### Phase 4: Playback
- Video player
- Direct play
- Progress tracking
- Resume functionality

### Phase 5: Advanced Features
- Transcoding
- HLS streaming
- Subtitles
- Audio tracks

### Phase 6: Admin & Polish
- Admin panel
- Settings management
- TV optimization
- PWA support

### Phase 7: Production Ready
- Docker optimization
- Documentation
- Testing
- Backup procedures

---

This architecture document provides the foundation for building Aether Media Server. Each section will be implemented in detail in subsequent phases.
