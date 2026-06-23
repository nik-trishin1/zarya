# Deploy zarya-tg to Railway

Step-by-step guide for production deployment.

## Is zarya allowed on Railway?

**Yes.** Railway prohibits **mirrors** and **userbots** — services that log in as a *human Telegram account* (unofficial APIs, scraping, relaying channels).

**zarya is not that.** It uses:

- Official **Telegram Bot API** (token from [@BotFather](https://t.me/BotFather), aiogram)
- Official **Telegram Mini App** (Web App SDK)

This is a normal web app + bot for event RSVP. Same category as any legitimate Bot API project. You can accept Railway's Fair Use Policy.

---

## After you log in to Railway — do this

### Step 0 — Prepare (2 minutes)

- [ ] Stop local `./scripts/dev-local.sh` (or leave `BOT_TOKEN` empty locally)
- [ ] Have BotFather **bot token** ready
- [ ] GitHub repo `zarya` is pushed to `main`

### Step 1 — New project + database

1. [railway.app](https://railway.app) → **New Project** → **Empty Project** (not "Deploy from GitHub" yet)
2. **+ New** → **Database** → **PostgreSQL** → wait until **Active**

> **Do not** deploy the whole `zarya` repo as one service from the root — Railway will run Railpack, fail with `start.sh not found`, and show `Railpack could not determine how to build the app`.

### Step 1b — If you already created a failed service from GitHub

Either **delete** that service, or fix it:

1. Open the failed service → **Settings**
2. **Root Directory:** `apps/zarya-tg/backend`
3. **Builder:** `Dockerfile` (not Railpack / Nixpacks)
4. **Dockerfile path:** `Dockerfile` (relative to root directory above)
5. **Deploy** → **Redeploy**

For frontend later: separate service, Root Directory = `apps/zarya-tg/frontend`.

### Step 2 — Backend

1. **+ New** → **GitHub Repo** → `zarya` (second service from same repo)
2. Click the new service → **Settings**:
   - **Root Directory:** `apps/zarya-tg/backend`
   - **Builder:** Dockerfile
3. **Networking** → **Generate Domain** → copy URL (e.g. `https://zarya-api-production.up.railway.app`)
4. **Variables** → add (use **Add Reference** for Postgres `DATABASE_URL`):

   | Variable | Value |
   |----------|--------|
   | `DATABASE_URL` | Reference → PostgreSQL → `DATABASE_URL` |
   | `BOT_TOKEN` | your BotFather token |
   | `ADMIN_TELEGRAM_IDS` | your Telegram ID (from @userinfobot for now) |
   | `API_BASE_URL` | backend domain from step 3 |
   | `WEBAPP_URL` | temporary: same as backend; update after frontend |
   | `UPLOAD_DIR` | `/app/uploads` |
   | `CORS_ORIGINS` | `https://web.telegram.org` (add frontend URL after step 3) |
   | `DEV_MODE` | `false` |
   | `SECRET_KEY` | any long random string |

5. **Volumes** → **Add Volume** → mount path `/app/uploads`
6. **Deploy** → wait for **Active** → open `https://your-api.../health` → `{"status":"ok"}`

### Step 3 — Frontend

1. **+ New** → **GitHub Repo** → `zarya`
2. **Settings** → **Root Directory:** `apps/zarya-tg/frontend`, **Builder:** Dockerfile
3. **Variables** → `VITE_API_URL` = backend URL from Step 2 (must be set **before** build)
4. **Networking** → **Generate Domain** → copy frontend URL
5. Deploy → open frontend URL in browser (should show zarya UI)

### Step 4 — Link services

1. **Backend** → Variables → update:
   - `WEBAPP_URL` = frontend URL
   - `CORS_ORIGINS` = `https://your-frontend.up.railway.app,https://web.telegram.org`
2. **Redeploy** backend and frontend

### Step 5 — Telegram

1. [@BotFather](https://t.me/BotFather) → `/setmenubutton` → your bot → Menu button URL = **frontend URL**
2. Open bot → tap menu button → Mini App should load
3. Send `/myid` → put ID in `ADMIN_TELEGRAM_IDS` on Railway → redeploy backend
4. Send `/admin` → inline buttons **Создать событие** / **Управлять событиями**

---

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

## Troubleshooting deploy

| Error | Fix |
|-------|-----|
| `Railpack could not determine how to build` / `start.sh not found` | Wrong builder. Set **Root Directory** (`apps/zarya-tg/backend` or `frontend`), **Builder = Dockerfile**, redeploy. Do not build from monorepo root. |
| `/health` fails | Backend not started — check Deploy logs |
| `/admin` «Нет доступа» | Fix `ADMIN_TELEGRAM_IDS` on Railway, redeploy |

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
