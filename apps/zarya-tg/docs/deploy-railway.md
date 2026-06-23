# Deploy zarya-tg to Railway

Step-by-step guide for production deployment.

## Is zarya allowed on Railway?

**Yes.** Railway prohibits **mirrors** and **userbots** — services that log in as a *human Telegram account* (unofficial APIs, scraping, relaying channels).

**zarya is not that.** It uses:

- Official **Telegram Bot API** (token from [@BotFather](https://t.me/BotFather), aiogram)
- Official **Telegram Mini App** (Web App SDK)

This is a normal web app + bot for event RSVP. Same category as any legitimate Bot API project. You can accept Railway's Fair Use Policy.

---

## Before you start

- [ ] GitHub repo `zarya` pushed to `main`, connected to Railway
- [ ] Bot token from [@BotFather](https://t.me/BotFather)
- [ ] Your Telegram ID ([@userinfobot](https://t.me/userinfobot) or `/myid` after first deploy)
- [ ] Stop local `./scripts/dev-local.sh` (or leave `BOT_TOKEN` empty locally)

**Important:** One `BOT_TOKEN` can only be used by **one** running backend. Do not run the same token locally and on Railway.

**Monorepo layout** — three separate Railway services, never deploy from repo root:

```
zarya/                         ← do NOT deploy from here
└── apps/zarya-tg/
    ├── backend/Dockerfile     ← backend service
    └── frontend/Dockerfile    ← frontend service
```

PostgreSQL is added as a **Database** template (no GitHub build).

---

## Recommended deploy (start here)

### Step 1 — Empty project + PostgreSQL

1. [railway.app](https://railway.app) → **New Project** → **Empty Project**
2. Do **not** choose "Deploy from GitHub" at this stage
3. **+ New** → **Database** → **PostgreSQL** → wait until **Active**

### Step 2 — Backend (API + bot)

1. **+ New** → **GitHub Repo** → select `zarya`
2. **Settings:**
   - **Root Directory:** `apps/zarya-tg/backend`
   - **Builder:** `Dockerfile`
3. **Networking** → **Generate Domain** → copy URL (e.g. `https://zarya-api-production.up.railway.app`)
4. **Variables:**

   | Variable | Value |
   |----------|--------|
   | `DATABASE_URL` | **Add Reference** → PostgreSQL → `DATABASE_URL` |
   | `BOT_TOKEN` | token from BotFather |
   | `ADMIN_TELEGRAM_IDS` | your Telegram ID |
   | `API_BASE_URL` | backend URL from step 3 |
   | `WEBAPP_URL` | temporary: backend URL; update after frontend |
   | `UPLOAD_DIR` | `/app/uploads` |
   | `CORS_ORIGINS` | `https://web.telegram.org` (add frontend URL in step 4) |
   | `DEV_MODE` | `false` |
   | `SECRET_KEY` | any long random string |

5. **Volumes** → **Add Volume** → mount path `/app/uploads`
6. **Deploy** → wait for **Active**
7. Check: `https://your-api.../health` → `{"status":"ok"}`

### Step 3 — Frontend (Mini App)

1. **+ New** → **GitHub Repo** → `zarya` (separate service)
2. **Settings:**
   - **Root Directory:** `apps/zarya-tg/frontend`
   - **Builder:** `Dockerfile`
3. **Variables:**

   | Variable | Value |
   |----------|--------|
   | `API_UPSTREAM` | backend **public** URL from Step 2 (e.g. `https://zarya-api-production.up.railway.app` or `zarya-api-production.up.railway.app`) |

   Do **not** use `.railway.internal` URLs. Do **not** paste the frontend URL here — only the backend.
   `https://` is optional — added automatically if missing.

4. **Networking** → **Generate Domain** → copy frontend URL (Railway sets `PORT` automatically — do not hardcode port 80)
5. **Deploy** → open frontend URL in browser (zarya UI should load)

`VITE_API_URL` is optional — leave empty; nginx proxies `/api` to `API_UPSTREAM` at runtime.

### Step 4 — Link backend and frontend

1. **Backend** → **Variables** → update:
   - `WEBAPP_URL` = frontend URL
   - `CORS_ORIGINS` = `https://your-frontend.up.railway.app,https://web.telegram.org`
2. **Redeploy** backend and frontend

### Step 5 — Telegram

1. [@BotFather](https://t.me/BotFather) → `/setmenubutton` → your bot → URL = **frontend URL**
2. Open bot → menu button → Mini App loads
3. `/myid` → verify ID → update `ADMIN_TELEGRAM_IDS` on Railway if needed → redeploy backend
4. `/admin` → inline buttons **Создать событие** / **Управлять событиями**

### Step 6 — Verify

#### 1. Проверка backend (health)

1. Откройте [railway.app](https://railway.app) → ваш проект
2. Кликните сервис **backend** (у вас может называться `zarya`)
3. Вкладка **Networking** → скопируйте **Public URL** (заканчивается на `.up.railway.app`)
4. Откройте **Safari или Chrome**
5. В адресную строку вставьте скопированный URL и **добавьте в конец** `/health`

   Пример: если URL `https://zarya-production-xxxx.up.railway.app`, откройте:

   `https://zarya-production-xxxx.up.railway.app/health`

6. Нажмите Enter

**Ожидаемый результат:** на белой странице текст `{"status":"ok"}`

Если видите ошибку 502/404 или HTML-страницу — backend не запущен или неверный URL. Смотрите **Deployments → View logs**.

| Check | Expected |
|-------|----------|
| API health | `https://your-api.../health` → `{"status":"ok"}` |
| Mini App | Bot menu button → event list |
| Admin | `/admin` → create event → appears in Mini App |

---

## Troubleshooting

### Railpack / `start.sh not found`

Railway tried to auto-build the monorepo root. Fix the existing service:

1. Open the failed service → **Settings**
2. **Root Directory:** `apps/zarya-tg/backend` (or `apps/zarya-tg/frontend` for frontend)
3. **Builder:** `Dockerfile` (not Railpack / Nixpacks)
4. **Dockerfile path:** `Dockerfile`
5. **Redeploy**

Or delete the failed service and follow **Recommended deploy** from Step 1.

### `/health` fails / Healthcheck failure

1. **Deploy logs** — open backend service → Deployments → latest → **View logs**. Common causes:
   - `Could not connect to database` → add `DATABASE_URL` reference to PostgreSQL service
   - `Token is invalid` → fix `BOT_TOKEN` (API should still start after redeploy with latest code)
   - App listening on wrong port → fixed in code: server uses Railway `PORT` env var
2. Confirm **Root Directory** = `apps/zarya-tg/backend`, **Builder** = Dockerfile
3. **Redeploy** after pulling latest `main`
4. Open `https://your-api.../health` manually in browser after deploy

### `/admin` — «Нет доступа»

Send `/myid`, put your ID in `ADMIN_TELEGRAM_IDS` on **Railway** (not local `.env`), redeploy backend.

### `/admin` — no response

Stop local backend using the same `BOT_TOKEN` — only one instance may poll Telegram.

### `/admin` — no buttons

Buttons are **inline**, below the message text (not a BotFather command menu).

### Frontend — «Application failed to respond» / healthcheck failure

1. **Variables** → `API_UPSTREAM` = `https://zarya-production-be.up.railway.app` (публичный URL backend)
   - Без этой переменной контейнер **сразу падает** → healthcheck failure
   - `VITE_API_URL` — не задавать
2. Подтяните последний `main` и **Redeploy** frontend
3. **Deployments → View logs** — должно быть:
   - `nginx listening on 0.0.0.0:...`
   - `proxying API to: https://...`
   - `configuration file ... test is successful`
4. Если в логах `ERROR: API_UPSTREAM is not set` — добавьте переменную и redeploy
5. Healthcheck проверяет `/nginx-health` (не зависит от backend)

### Mini App empty / `Unexpected token '<'` / «is not valid JSON»

Браузер запрашивает `/api/events`, а вместо JSON приходит HTML (`<!doctype...`). Значит frontend не проксирует запросы на backend.

1. **Frontend** → **Variables** → `API_UPSTREAM` = **публичный** URL backend (`.up.railway.app`, без `/` в конце)
2. Убедитесь, что в `API_UPSTREAM` **не** frontend URL и **не** `.railway.internal`
3. **Redeploy** frontend (после изменения переменной)
4. Откройте frontend URL в браузере — должен загрузиться интерфейс zarya без ошибки JSON

Также проверьте на **backend**: `WEBAPP_URL` = frontend URL, `CORS_ORIGINS` включает frontend URL.

### `/start` — нет ответа / нет кнопок

**Важно:** у zarya **нет** меню команд внизу (как у `/help`). Кнопки — **под текстом сообщения** (inline).

1. Отправьте `/myid` — если **нет ответа вообще**, бот не работает:
   - **Backend** → **Variables** → `BOT_TOKEN` задан (формат `123456789:AAH...`)
   - Остановите локальный `./scripts/dev-local.sh` — один токен = один процесс
   - **Deployments → View logs** → ищите `Telegram bot polling started`
2. Если `/myid` отвечает, а `/start` нет — redeploy backend с последним `main`
3. `WEBAPP_URL` на backend = **публичный HTTPS** frontend (не localhost, не `.internal`)
4. Кнопка **внизу экрана** чата (menu button) — отдельно: [@BotFather](https://t.me/BotFather) → `/setmenubutton` → URL frontend

### Mini App empty (старая диагностика)

Check `WEBAPP_URL`, `API_UPSTREAM`, `CORS_ORIGINS`; ensure `DEV_MODE=false` on production.

---

## Local vs production

| | Local | Production |
|---|-------|------------|
| `BOT_TOKEN` | Empty (browser dev) | Railway Variables |
| Database | SQLite | PostgreSQL |
| `DEV_MODE` | `true` | `false` |
| Mini App URL | `http://localhost:5173` | Railway frontend domain |
