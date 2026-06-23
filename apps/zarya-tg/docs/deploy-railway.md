# Deploy zarya-tg to Railway

Step-by-step guide for production deployment.

## Before you start

- GitHub repo connected to Railway
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your Telegram user ID (send `/myid` to the bot after first deploy, or ask [@userinfobot](https://t.me/userinfobot))

**Important:** One `BOT_TOKEN` can only be used by **one** running backend. If Railway and your laptop both run the bot with the same token, `/admin` and other commands will behave unpredictably. For production, stop local `dev-local.sh` or leave `BOT_TOKEN` empty locally.

---

## 1. Create Railway project

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub → select `zarya`
2. You will create **3 services**: PostgreSQL, backend, frontend

---

## 2. PostgreSQL

1. New → Database → PostgreSQL
2. Open the PostgreSQL service → **Variables** → copy `DATABASE_URL`  
   Railway provides `postgresql://...` — the backend accepts this URL as-is (async driver is configured automatically).

---

## 3. Backend service

1. New → GitHub Repo → same repo
2. **Settings → Root Directory:** `apps/zarya-tg/backend`
3. **Settings → Builder:** Dockerfile (`Dockerfile` in that folder)
4. **Settings → Networking → Generate Domain** (e.g. `zarya-api.up.railway.app`)

### Variables (backend)

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Reference from PostgreSQL plugin |
| `BOT_TOKEN` | `7123456789:AAH...` | From BotFather |
| `ADMIN_TELEGRAM_IDS` | `12345678` | Your real ID from `/myid` |
| `WEBAPP_URL` | `https://zarya-web.up.railway.app` | Frontend public URL |
| `API_BASE_URL` | `https://zarya-api.up.railway.app` | This backend public URL |
| `UPLOAD_DIR` | `/app/uploads` | |
| `CORS_ORIGINS` | `https://zarya-web.up.railway.app,https://web.telegram.org` | |
| `DEV_MODE` | `false` | |
| `SECRET_KEY` | random string | |

### Volume (cover images)

1. Backend service → **Volumes** → Add Volume  
2. Mount path: `/app/uploads`

### Health check

Railway should use `/health` — configured in `railway.toml`.

---

## 4. Frontend service

1. New → GitHub Repo → same repo
2. **Settings → Root Directory:** `apps/zarya-tg/frontend`
3. **Settings → Builder:** Dockerfile

### Build variable

| Variable | Example |
|----------|---------|
| `VITE_API_URL` | `https://zarya-api.up.railway.app` |

Set as **build-time** variable (Railway → Variables → add before deploy).

4. **Networking → Generate Domain** (e.g. `zarya-web.up.railway.app`)
5. Redeploy frontend after you have the final backend URL.

---

## 5. Configure Telegram bot

In [@BotFather](https://t.me/BotFather):

1. `/setmenubutton` → select your bot → URL = `https://zarya-web.up.railway.app`
2. Optional: `/setdescription` — short Russian description of zarya

---

## 6. Verify

| Check | URL / action |
|-------|----------------|
| API health | `https://zarya-api.up.railway.app/health` → `{"status":"ok"}` |
| Mini App | Open bot → menu button → event list loads |
| Admin | `/myid` → copy ID → set `ADMIN_TELEGRAM_IDS` on Railway → redeploy → `/admin` → buttons **Создать событие** / **Управлять событиями** |
| Create event | `/admin` → create → event appears in Mini App |

---

## Troubleshooting `/admin`

| Symptom | Fix |
|---------|-----|
| «Нет доступа» | Send `/myid`, put ID in `ADMIN_TELEGRAM_IDS` on **Railway** (not only local `.env`), redeploy backend |
| No response at all | Stop local backend with same `BOT_TOKEN`; only one instance may poll |
| No buttons under message | `/admin` uses **inline buttons** below the text, not a command menu — scroll to the message |
| Mini App empty | Check `WEBAPP_URL`, `VITE_API_URL`, `CORS_ORIGINS`; set `DEV_MODE=false` on prod |

---

## Local vs production

| | Local | Production |
|---|-------|------------|
| `BOT_TOKEN` in `.env` | Empty (browser dev) or dev-only bot | Set on Railway only |
| Database | SQLite file | PostgreSQL on Railway |
| `DEV_MODE` | `true` | `false` |
| Mini App URL | `http://localhost:5173` | Railway frontend domain |
