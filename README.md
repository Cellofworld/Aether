# Aether Media Server

Полноценный домашний медиасервер с современным веб-интерфейсом, вдохновленный Jellyfin/Plex.

## Возможности

- 📁 **Автоматическое сканирование** библиотек (фильмы, сериалы, аниме, мультфильмы)
- 🎬 **Красивая библиотека** с постерами, описаниями, рейтингами и метаданными
- ▶️ **Воспроизведение в браузере** с поддержкой субтитров и аудиодорожек
- 📺 **Smart TV-friendly** интерфейс с управлением с пульта
- ⏸️ **Продолжение просмотра** с места остановки
- 🔍 **Поиск** по всей медиатеке
- 📂 **Категории и фильтры**
- 👤 **Авторизация** и разделение пользователей
- 🔄 **Автоматическое обновление** библиотеки
- 🌐 **Работа в локальной сети**
- 🐳 **Docker Compose** для простого запуска

## Быстрый старт

### Требования

- Docker и Docker Compose
- Минимум 2GB RAM
- Место на диске для медиафайлов

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url> aether-media-server
cd aether-media-server
```

2. Создайте файл `.env`:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` и укажите:
- `TMDB_API_KEY` - API ключ от The Movie Database (бесплатно на themoviedb.org)
- `JWT_SECRET` - случайная строка для JWT токенов
- `MEDIA_ROOT` - путь к вашей медиатеке (по умолчанию `/media`)

4. Запустите сервер:
```bash
docker compose up -d
```

5. Откройте в браузере:
```
http://localhost:80
```

Или по IP вашего сервера:
```
http://192.168.1.XX
```

### Учетные данные по умолчанию

- **Логин**: `admin`
- **Пароль**: `admin123`

## Структура проекта

```
aether-media-server/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Конфигурация, безопасность
│   │   ├── models/    # SQLAlchemy модели
│   │   ├── schemas/   # Pydantic схемы
│   │   ├── services/  # Бизнес-логика
│   │   ├── workers/   # Фоновые задачи (сканер)
│   │   └── main.py    # Точка входа
│   ├── migrations/    # Alembic миграции
│   └── requirements.txt
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   └── types/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Настройка библиотек

После первого входа:

1. Перейдите в **Админка** → **Библиотеки**
2. Нажмите **Добавить библиотеку**
3. Выберите тип (Фильмы, Сериалы, Аниме, etc.)
4. Укажите путь к папке с медиа (например, `/media/movies`)
5. Нажмите **Сохранить**
6. Запустите **Сканирование**

### Рекомендуемая структура папок

```
/media/
├── movies/
│   ├── Interstellar (2014)/
│   │   └── Interstellar.2014.1080p.mkv
│   └── The Matrix (1999)/
│       └── The.Matrix.1999.4K.mkv
├── series/
│   ├── Breaking Bad/
│   │   ├── Season 01/
│   │   │   ├── S01E01.mkv
│   │   │   └── S01E02.mkv
│   │   └── Season 02/
│   └── The Mandalorian/
└── anime/
```

## API Документация

После запуска API документация доступна по адресу:
```
http://localhost:80/api/docs
```

### Основные endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/login` | Вход |
| GET | `/api/libraries` | Список библиотек |
| GET | `/api/movies` | Фильмы |
| GET | `/api/series` | Сериалы |
| GET | `/api/search?q=` | Поиск |
| GET | `/api/playback/continue` | Продолжить просмотр |
| POST | `/api/playback/progress` | Обновить прогресс |
| POST | `/api/admin/scan` | Запустить сканирование |

## Управление воспроизведением

### Клавиатура / Пульт

| Кнопка | Действие |
|--------|----------|
| ← → | Навигация / Перемотка |
| ↑ ↓ | Навигация |
| Enter / Space | Выбрать / Play-Pause |
| Escape / Back | Назад |
| Shift + ← | -10 секунд |
| Shift + → | +10 секунд |

## Транскодинг

Сервер поддерживает:

- **Direct Play** - если устройство поддерживает формат
- **Remux** - смена контейнера без перекодирования
- **Transcoding** - полное перекодирование через FFmpeg

### Настройка транскодинга

В `.env`:
```
TRANSCODING_ENABLED=true
HARDWARE_ACCELERATION=none  # none, nvidia, vaapi, qsv
```

### Аппаратное ускорение

#### NVIDIA NVENC
```
HARDWARE_ACCELERATION=nvidia
```

#### Intel Quick Sync
```
HARDWARE_ACCELERATION=qsv
```

#### VAAPI (AMD/Intel)
```
HARDWARE_ACCELERATION=vaapi
```

## Резервное копирование

Что нужно бэкапить:

1. **База данных PostgreSQL**:
```bash
docker compose exec postgres pg_dump -U aether aether_db > backup.sql
```

2. **Папка с настройками**:
```bash
tar -czf settings-backup.tar.gz ./backend/app/data
```

Медиафайлы не требуют бэкапа через приложение.

## Troubleshooting

### Сервер не запускается

Проверьте логи:
```bash
docker compose logs -f
```

### Ошибки сканирования

Убедитесь, что:
- Пути к медиа указаны правильно
- У контейнера есть доступ к файлам
- Форматы файлов поддерживаются

### Проблемы с воспроизведением

- Проверьте поддержку кодеков вашим устройством
- Включите транскодинг в настройках
- Попробуйте другой браузер

## Smart TV Setup

1. Откройте браузер на TV
2. Перейте по адресу сервера (например, `http://192.168.1.100`)
3. Используйте пульт для навигации:
   - Стрелки для перемещения
   - OK/Enter для выбора
   - Back/Return для возврата

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Технологии

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- FFmpeg
- Pydantic

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- React Router
- TanStack Query

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создавайте Issues на GitHub.
