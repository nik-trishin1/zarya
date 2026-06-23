# zarya-tg — Local Development & Deployment

## Prerequisites

- **Python 3.10–3.13** (**3.12 recommended**). Do **not** use macOS system Python 3.9 or Python 3.14 — dependencies won't install.
- **Node.js 20+** with `npm` in PATH
- Telegram Bot Token from [@BotFather](https://t.me/BotFather) (optional for browser-only local testing)
- Docker — **optional** (only if you prefer `docker compose`)

### macOS setup (first time)

**No Homebrew?** Install from [python.org](https://www.python.org/downloads/release/python-3120/) — **Python 3.12** `.pkg` (not 3.14). Then [Node.js](https://nodejs.org/en/download) LTS `.pkg`. Restart Terminal after each install.

If you previously ran with system Python 3.9, delete the old virtualenv first:

```bash
rm -rf apps/zarya-tg/backend/.venv
```

**With Homebrew:**

```bash
brew install python@3.11 node
```

After install, make sure `npm` is in PATH:

```bash
node -v   # should print v20+
npm -v
```

If `npm` is not found after Homebrew install:

```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Without Homebrew — nvm:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.zshrc
nvm install 20
nvm use 20
```

If you use **nvm** or **fnm**, open a regular terminal first — `dev-local.sh` tries to load them automatically. As a fallback:

```bash
./scripts/dev-local.sh --backend-only   # API only, no frontend
```

---

## Quick Start without Docker (recommended for macOS)

From the repository root:

```bash
cd apps/zarya-tg
chmod +x scripts/dev-local.sh
./scripts/dev-local.sh
```

Or step by step in **two terminals**:

### Terminal 1 — Backend

```bash
cd apps/zarya-tg/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # SQLite + DEV_MODE=true by default
python run.py
```

### Terminal 2 — Frontend

```bash
cd apps/zarya-tg/frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173 in the browser.

- API health check: http://localhost:8000/health
- Local DB file: `apps/zarya-tg/backend/zarya.db` (SQLite, created automatically)
- `DEV_MODE=true` lets the API work in a regular browser without Telegram `initData`

> **Note:** Admin bot commands (`/admin`) require a real `BOT_TOKEN` in `backend/.env`. The Mini App UI works in the browser without it.

---

## Quick Start with Docker (optional)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

```bash
cd apps/zarya-tg

export BOT_TOKEN=your-bot-token
export ADMIN_TELEGRAM_IDS=your-telegram-id
export WEBAPP_URL=http://localhost:5173
export API_BASE_URL=http://localhost:8000

docker compose up --build
```

If you see `command not found: docker`, install Docker Desktop or use the **without Docker** instructions above.

---

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Set the Mini App URL: `/setmenubutton` → your frontend URL
3. Add to `backend/.env`:
   ```
   BOT_TOKEN=your-token
   ADMIN_TELEGRAM_IDS=your-telegram-numeric-id
   DEV_MODE=false
   ```
4. Send `/admin` to manage events, `/start` to open the app

To find your Telegram ID, message [@userinfobot](https://t.me/userinfobot).

---

## Railway Deployment

**Full guide:** [docs/deploy-railway.md](docs/deploy-railway.md)

Quick summary: 3 services on Railway (PostgreSQL + backend + frontend). Set `ADMIN_TELEGRAM_IDS` to your real Telegram ID from `/myid`. Do not run the same `BOT_TOKEN` locally and on Railway at the same time.

---

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

All API endpoints (except `/health`) require `X-Telegram-Init-Data` header (skipped when `DEV_MODE=true`).

---

## Running Tests

```bash
cd apps/zarya-tg/backend
pip install -r requirements.txt
pytest
```
