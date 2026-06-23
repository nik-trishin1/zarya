# zarya-tg — Local Development & Deployment

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## Quick Start with Docker

```bash
cd apps/zarya-tg

# Create .env in repo root or export variables
export BOT_TOKEN=your-bot-token
export ADMIN_TELEGRAM_IDS=your-telegram-id
export WEBAPP_URL=http://localhost:5173
export API_BASE_URL=http://localhost:8000

docker compose up --build
```

- API: http://localhost:8000
- Mini App: http://localhost:5173
- Health: http://localhost:8000/health

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL locally or use Docker for DB only:
# docker run -d -p 5432:5432 -e POSTGRES_USER=zarya -e POSTGRES_PASSWORD=zarya -e POSTGRES_DB=zarya postgres:16-alpine

cp .env.example .env
# Edit .env with your values

python run.py
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Set the Mini App URL: `/setmenubutton` → your frontend URL
3. Set `BOT_TOKEN` and `ADMIN_TELEGRAM_IDS` in environment
4. Send `/admin` to manage events, `/start` to open the app

## Railway Deployment

Deploy two services on Railway:

1. **Backend** — use `apps/zarya-tg/backend/Dockerfile`, attach PostgreSQL plugin, set env vars
2. **Frontend** — use `apps/zarya-tg/frontend/Dockerfile` with `VITE_API_URL` build arg pointing to backend URL

Required environment variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (auto from Railway plugin) |
| `BOT_TOKEN` | Telegram bot token |
| `ADMIN_TELEGRAM_IDS` | Comma-separated admin Telegram user IDs |
| `WEBAPP_URL` | Public URL of the frontend |
| `API_BASE_URL` | Public URL of the backend |
| `UPLOAD_DIR` | `/app/uploads` (mount a volume) |
| `CORS_ORIGINS` | Frontend URL(s) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/events` | List upcoming events |
| GET | `/api/events/{id}` | Event details |
| GET | `/api/registrations/my` | User's registrations |
| POST | `/api/registrations/{id}` | Register for event |
| DELETE | `/api/registrations/{id}` | Cancel registration |
| GET | `/api/events/{id}/calendar` | Download .ics file |

All API endpoints (except `/health`) require `X-Telegram-Init-Data` header.

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```
