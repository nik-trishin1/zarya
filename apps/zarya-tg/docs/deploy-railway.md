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
   | `UPLOAD_DIR` | `/app/uploads` (legacy disk cache; optional) |
   | `CORS_ORIGINS` | `https://web.telegram.org` (add frontend URL in step 4) |
   | `DEV_MODE` | `false` |
   | `SECRET_KEY` | any long random string |

5. **Deploy** → wait for **Active** (cover images are stored in PostgreSQL — no volume required)
6. Check: `https://your-api.../health` → `{"status":"ok"}`

### Step 3 — Frontend (Mini App)

1. **+ New** → **GitHub Repo** → `zarya` (separate service)
2. **Settings:**
   - **Root Directory:** `apps/zarya-tg/frontend`
   - **Builder:** `Dockerfile`
3. **Variables:**

   | Variable | Value |
   |----------|--------|
   | `API_UPSTREAM` | backend **public** URL from Step 2 (e.g. `https://zarya-api-production.up.railway.app` or `zarya-api-production.up.railway.app`) |
   | `VITE_BOT_USERNAME` | `zarya_friends_bot` (production bot **@zarya_friends_bot**; used in share deep links, baked in at Docker build) |

   Do **not** use `.railway.internal` URLs. Do **not** paste the frontend URL here — only the backend.
   `https://` is optional — added automatically if missing.

4. **Networking** → **Generate Domain** → copy frontend URL (Railway sets `PORT` automatically — do not hardcode port 80)
5. **Deploy** → open frontend URL in browser (zarya UI should load)

`VITE_API_URL` is optional — leave empty; nginx proxies `/api` to `API_UPSTREAM` at runtime.

`VITE_BOT_USERNAME` must match your Telegram bot handle (without `@`). Share links use `https://t.me/{username}?startapp=event_{id}`. Default: `zarya_friends_bot`.

Optional `VITE_BOT_APP_SHORT_NAME` — only if you configured a Direct Link Mini App in BotFather (helps some iOS clients open the app instead of Safari).

### Step 4 — Link backend and frontend

1. **Backend** → **Variables** → update:
   - `WEBAPP_URL` = frontend URL
   - `CORS_ORIGINS` = `https://your-frontend.up.railway.app,https://web.telegram.org`
2. **Redeploy** backend and frontend

### Step 5 — Telegram Mini App (настройка в BotFather)

Mini App открывается **только внутри Telegram**, не в Safari/Chrome.

1. **Backend** → `WEBAPP_URL` = `https://zarya-production-fe.up.railway.app` (ваш frontend, HTTPS)
2. **Backend** → `CORS_ORIGINS` = `https://zarya-production-fe.up.railway.app,https://web.telegram.org`
3. **Redeploy backend** после смены переменных
4. [@BotFather](https://t.me/BotFather) → `/mybots` → ваш бот → **Bot Settings** → раздел Mini App:

   **Menu Button** (кнопка слева внизу в чате с ботом):
   - Выберите **Enter URL**
   - URL: `https://zarya-production-fe.up.railway.app`
   - **Enter Title**: например `zarya` или `Открыть zarya`

   **Main App** (кнопка запуска в профиле бота):
   - **Enter URL**: тот же `https://zarya-production-fe.up.railway.app`
   - **Launch Mode**: **Fullsize** (полноэкранный Mini App внутри Telegram)

   **Direct Links** — опционально, для MVP не обязательно.

5. Закройте и снова откройте чат с ботом в Telegram (или перезапустите Telegram)
6. `/start` → приветственное сообщение (Mini App открывается через **Menu Button**)
7. `/myid` → ваш ID → `ADMIN_TELEGRAM_IDS` на Railway → redeploy backend

**Если открывается браузер, а не Mini App:**
- `WEBAPP_URL` на backend ≠ frontend URL или без `https://` → redeploy backend
- В BotFather не настроен **Menu Button** → **Enter URL** (не Disabled)
- Открываете ссылку в Safari, а не через кнопку в Telegram

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

### Frontend — «Application failed to respond» / 502 (deploy Active, URL не открывается)

Частая причина: в **Networking** домен направлен на **порт 80**, а Railway задаёт `PORT=8080`.

**Быстрое исправление (без кода):**
1. Frontend → **Settings** → **Networking**
2. Откройте ваш домен `zarya-production-fe.up.railway.app`
3. Поле **Port** → поставьте **8080** (или удалите домен и **Generate Domain** заново — порт подставится автоматически)
4. Сохраните и подождите 1–2 минуты

**После redeploy с последним `main`:** nginx слушает и `PORT`, и **80** — должно работать даже при порте 80 в Networking.

В логах deploy ищите:
```
nginx listening on 0.0.0.0:8080, 0.0.0.0:80, proxying API to: https://...
```

### Frontend — healthcheck failure

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

### Обложка события не отображается (битая картинка)

**С версии с хранением в PostgreSQL** новые обложки сохраняются в базе и **не пропадают при redeploy**. Volume для `/app/uploads` больше не обязателен.

1. **Redeploy backend** с последним `main` (нужна таблица `media_files`)
2. События со **старыми** URL `/uploads/...` (до миграции) — один раз **перезагрузите обложку** в боте (редактировать → новое фото). Новый URL будет `/media/...` и сохранится навсегда
3. Если файла нет — оранжевая градиент-заглушка (это нормально)
4. Проверка API: `https://ваш-backend.../health` → `{"status":"ok"}`
5. Проверка media (после загрузки): `https://ваш-frontend.../media/<id>` → 200, `image/jpeg`

**Legacy:** volume на `/app/uploads` нужен только для старых файлов в формате `/uploads/...`; для новых загрузок не требуется.

### Mini App в Telegram показывает старую версию (в браузере уже новая)

Telegram WebView **агрессивно кэширует** Mini App. Браузер и бот могут показывать разное, пока не обновлён frontend.

1. **Redeploy frontend** с последним `main` (в nginx отключён кэш для `index.html`)
2. Полностью **закройте** чат с ботом и откройте Mini App заново (или перезапустите Telegram)
3. На iOS: иногда помогает «Потянуть вниз» для обновления внутри Mini App
4. Проверка заголовков (после redeploy):
   ```bash
   curl -sI https://zarya-production-fe.up.railway.app/ | grep -i cache
   ```
   Ожидается `Cache-Control: no-cache` для `index.html`

### Mini App empty / `Unexpected token '<'` / «API вернул неверный ответ»

nginx проксировал API с неверным заголовком `Host` (frontend вместо backend) — Railway зависал и отдавал HTML.

1. Подтяните последний `main` и **Redeploy frontend**
2. **Variables** → `API_UPSTREAM` = `https://zarya-production-be.up.railway.app`
3. **Удалите** `VITE_API_URL`, если задан
4. Проверка: `https://ваш-frontend.up.railway.app/api/events` → JSON `{"detail":"Missing Telegram init data"}` (это нормально в браузере)

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
