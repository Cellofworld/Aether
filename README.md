# Aether Media Server

A self-hosted home media server inspired by Jellyfin/Plex, built with modern technologies.

## Features

- 🎬 **Media Library Management** - Automatic scanning of movies, series, anime, cartoons
- 📺 **Smart TV Support** - Remote-friendly UI with keyboard navigation
- 🎥 **Video Streaming** - Direct play and transcoding support (HLS)
- 📝 **Subtitles & Audio Tracks** - Multiple language support
- ⏯️ **Resume Playback** - Continue watching from where you left off
- 🔍 **Search & Filters** - Find content quickly
- 📊 **Metadata** - Automatic metadata from TMDB (posters, descriptions, ratings)
- 👥 **User Management** - Multi-user support with roles
- 🐳 **Docker Ready** - Easy deployment with Docker Compose

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│  Frontend   │     │   Backend   │
│   (Port 80) │     │   (React)   │◀───▶│  (Fastify)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │  PostgreSQL │
                                        │  Database   │
                                        └─────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- FFmpeg (for transcoding)

### Docker Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aether-media-server
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set your JWT_SECRET and TMDB_API_KEY
   ```

3. **Get TMDB API Key** (optional but recommended)
   - Visit https://www.themoviedb.org/settings/api
   - Create an account and generate an API key
   - Add it to your `.env` file

4. **Start the services**
   ```bash
   docker compose up -d
   ```

5. **Access the application**
   - Open http://localhost (or http://YOUR_SERVER_IP)
   - Default admin credentials: `admin@aether.local` / `admin123`

### Local Development

```bash
# Backend
cd backend
npm install
npm run db:generate
npm run dev

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Directory Structure

```
aether-media-server/
├── backend/           # Node.js + Fastify API
│   ├── src/
│   │   ├── routes/    # API endpoints
│   │   ├── services/  # Business logic
│   │   ├── middleware/# Auth, CORS, etc.
│   │   └── config/    # Database, settings
│   ├── prisma/        # Database schema
│   └── Dockerfile
├── frontend/          # React + TypeScript UI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   └── Dockerfile
├── nginx/             # Reverse proxy config
├── docker-compose.yml
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | (required) |
| `JWT_SECRET` | Secret for JWT tokens | (required) |
| `TMDB_API_KEY` | The Movie Database API key | (optional) |
| `MEDIA_ROOT` | Path to media files | `/media` |
| `TRANSCODE_ROOT` | Path for transcoding temp files | `/transcode` |
| `LOG_LEVEL` | Logging level | `info` |
| `SCAN_ON_STARTUP` | Scan libraries on startup | `true` |

### Hardware Acceleration

For GPU-accelerated transcoding, set in `.env`:

```bash
# NVIDIA GPU
HARDWARE_ACCELERATION=nvidia

# Intel Quick Sync
HARDWARE_ACCELERATION=qsv

# VAAPI (AMD/Intel)
HARDWARE_ACCELERATION=vaapi
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Libraries
- `GET /api/libraries` - List all libraries
- `GET /api/libraries/:id` - Get library details
- `POST /api/libraries` - Create library (admin)
- `GET /api/libraries/:id/items` - Get library items

### Media
- `GET /api/movies` - List movies
- `GET /api/movies/:id` - Get movie details
- `GET /api/series` - List series
- `GET /api/series/:id` - Get series details
- `GET /api/series/:id/seasons` - Get seasons
- `GET /api/seasons/:id/episodes` - Get episodes

### Playback
- `POST /api/playback/progress` - Update watch progress
- `GET /api/playback/continue-watching` - Get continue watching list
- `GET /api/playback/watchlist` - Get watchlist
- `POST /api/playback/watchlist/:id` - Toggle watchlist

### Search
- `GET /api/search?q=query` - Search content

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `GET /api/admin/jobs` - List scan jobs
- `POST /api/admin/scan/:libraryId` - Start library scan
- `GET /api/admin/users` - List users (admin)

## Smart TV Usage

The interface is optimized for TV use:

- **Arrow Keys** - Navigate
- **Enter** - Select/Play
- **Back/Esc** - Go back
- **Space** - Play/Pause
- **Left/Right** - Seek ±10 seconds

## Troubleshooting

### Database Connection Issues
```bash
docker compose logs postgres
docker compose restart postgres
```

### Scanner Not Finding Media
- Ensure media paths are correctly mounted in docker-compose.yml
- Check file permissions: `chmod -R 755 /path/to/media`
- Run manual scan from admin panel

### Transcoding Issues
- Verify FFmpeg is installed in backend container
- Check available disk space in transcode volume
- Review logs: `docker compose logs backend`

## Backup

Backup these volumes regularly:
```bash
# Database
docker compose exec postgres pg_dump -U aether aether_db > backup.sql

# Or backup the entire postgres_data volume
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines first.
