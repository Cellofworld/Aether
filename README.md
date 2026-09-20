# 🎬 Aether Media Server

A modern, self-hosted media server inspired by Jellyfin/Plex, built with Node.js, React, and PostgreSQL.

![Aether Media Server](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **📚 Media Library Management** - Organize movies, TV shows, anime, and more
- **🎭 Rich Metadata** - Automatic metadata from TMDB (posters, descriptions, ratings)
- **📺 Smart TV Friendly** - Optimized UI for TV browsers and remote controls
- **▶️ Video Playback** - Direct play with resume functionality
- **🔍 Search & Filter** - Find content quickly with powerful search
- **👥 Multi-User Support** - Individual watch progress and playlists
- **📱 Responsive Design** - Works on desktop, tablet, mobile, and TV
- **🐳 Docker Ready** - Easy deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- FFmpeg (for transcoding, optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/aether-media-server.git
   cd aether-media-server
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and set your values:**
   - Change `JWT_SECRET` to a random string
   - Add your TMDB API key (optional, get from https://www.themoviedb.org)
   - Set `MEDIA_ROOT` to your media directory

4. **Start the server:**
   ```bash
   docker compose up -d
   ```

5. **Access the application:**
   - Open http://localhost in your browser
   - Default admin credentials: `admin@aether.local` / `admin123`

## 📁 Directory Structure

```
aether-media-server/
├── backend/           # Node.js + Fastify API
│   ├── src/
│   │   ├── config/    # Configuration
│   │   ├── routes/    # API routes
│   │   └── index.ts   # Entry point
│   ├── prisma/        # Database schema
│   └── Dockerfile
├── frontend/          # React + TypeScript UI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── Dockerfile
├── nginx/             # Nginx configuration
├── docker-compose.yml
└── README.md
```

## 🗄️ Database Schema

The application uses PostgreSQL with Prisma ORM:

- **Users** - Authentication and authorization
- **Libraries** - Media collections (Movies, TV Shows, etc.)
- **MediaItems** - Movies and Series with metadata
- **Seasons/Episodes** - TV show structure
- **VideoFiles** - Physical file information
- **WatchProgress** - Resume playback tracking
- **WatchHistory** - Viewing history
- **Watchlist** - User favorites

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | Secret for JWT tokens | Required |
| `TMDB_API_KEY` | TheMovieDB API key | Optional |
| `MEDIA_ROOT` | Path to media files | `/media` |
| `PORT` | Backend port | `3000` |
| `LOG_LEVEL` | Logging level | `info` |

### Media Libraries

Supported library types:
- MOVIES
- SERIES
- ANIME
- CARTOONS
- DOCUMENTARIES
- MUSIC
- PHOTOS

## 📺 Smart TV Usage

The interface is optimized for TV use:

- **Arrow Keys** - Navigate between items
- **Enter/OK** - Select/Play
- **Back/Escape** - Go back
- **Space** - Play/Pause
- **Left/Right** - Seek in player

### Tips for TV:
1. Use a modern TV browser (WebOS, Tizen, Android TV)
2. Connect via LAN for best performance
3. Use direct play when possible (no transcoding)

## 🔌 API Endpoints

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
- `GET /api/series/:id` - Get series with seasons/episodes
- `GET /api/episodes/:id` - Get episode details

### Playback
- `POST /api/playback/progress` - Update watch progress
- `GET /api/playback/continue-watching` - Get continue watching list
- `GET /api/playback/history` - Get watch history
- `POST /api/playback/watchlist/:id` - Toggle watchlist

### Search
- `GET /api/search?q=query` - Global search

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `GET /api/admin/jobs` - List scan jobs
- `POST /api/admin/scan/:libraryId` - Start library scan
- `GET /api/admin/users` - List users (admin)

## 🛠️ Development

### Backend

```bash
cd backend
npm install
npm run dev
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
npx prisma migrate dev
npx prisma generate
```

### Seed Data

```bash
cd backend
npm run prisma:seed
```

Default users after seeding:
- Admin: `admin@aether.local` / `admin123`
- User: `user@aether.local` / `user123`

## 🎥 Video Streaming

Aether supports multiple streaming methods:

1. **Direct Play** - Original file served directly (best quality)
2. **Direct Stream** - Remuxing container only
3. **Transcoding** - Full video/audio transcoding (requires FFmpeg)

### Supported Formats

**Video:** MP4, MKV, AVI, MOV, WebM
**Audio:** AAC, AC3, EAC3, DTS, FLAC, MP3
**Subtitles:** SRT, ASS, SSA, WebVTT

## 🔒 Security

- Password hashing with bcrypt
- JWT-based authentication
- Role-based access control (Admin/User)
- CORS protection
- Input validation with Zod
- SQL injection prevention (Prisma ORM)

## 📊 System Requirements

**Minimum:**
- 2 GB RAM
- Dual-core CPU
- 10 GB storage

**Recommended:**
- 4+ GB RAM
- Quad-core CPU
- SSD for database
- Hardware acceleration for transcoding (optional)

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
docker compose logs backend
# Check DATABASE_URL and JWT_SECRET in .env
```

**No metadata/posters:**
- Add TMDB_API_KEY to .env
- Restart backend container

**Video playback issues:**
- Check MEDIA_ROOT path permissions
- Verify file format compatibility
- Check browser console for errors

**Database connection failed:**
```bash
docker compose restart postgres
docker compose logs postgres
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 🙏 Acknowledgments

- Inspired by Jellyfin and Plex
- Metadata provided by TheMovieDB
- Built with Fastify, React, and Prisma
