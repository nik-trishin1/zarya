# zarya-tg — Handoff Summary (Chat Transfer)

Last updated: 2026-07-16

This document captures key context and completed work so a new session/chat can continue seamlessly.

## Current Product Scope

- App: Telegram Mini App for community events (`apps/zarya-tg/`)
- MVP features: event browsing, registration/cancellation, calendar export, admin via bot, Russian-only UI
- Stack: React 18 + TS (frontend), FastAPI + aiogram (backend), Postgres, Railway (Docker)

## Recent Changes (Highlights)

- Deep links and sharing
  - Event deep links now use both parameters for reliability across iOS/Android:
    - Format (Main Mini App): `https://t.me/{bot}?startapp=event_{id}&startApp=event_{id}`
    - Optional Direct Link (with short name): `https://t.me/{bot}/{short_name}?startapp=event_{id}&startApp=event_{id}`
  - Frontend share opens native Telegram share sheet via `t.me/share/url?url=...&text=...` (prevents Safari on iOS).
  - Production bot handle: `@zarya_friends_bot` (`VITE_BOT_USERNAME=zarya_friends_bot`).
  - Optional Direct Link short name supported via `VITE_BOT_APP_SHORT_NAME` / `BOT_APP_SHORT_NAME`.

- Admin announcements and broadcasts
  - New-event announcement to all users after create (ADR-011) — fixed NameError in bulk delivery.
  - New: Admin broadcast to all bot users from `/admin` (ADR-017) — “📢 Написать всем” flow with preview + confirm.
  - Participant broadcast (ADR-007) retained for per-event registrants.

- Reminders
  - 24h reminder scheduler (ADR-013): hourly tick, 08:00–22:00 MSK, immediate cancel inline button.
  - Startup delay added (60s) to avoid contention at deploy; background tasks start after DB is ready.

- Capacity and UI
  - Event capacity limit (`max_participants`, `is_full`) with blocking at full.
  - Guest count label on frontend: always shows “+ Плюша”, e.g. “Гостей: 1 из 20 + Плюша” or “Гостей: 1 + Плюша”.

- Deploy/Infra
  - `.dockerignore` added for backend and frontend to slim Railway builds.
  - Backend starts bot + scheduler after DB migration completes (FastAPI lifespan).
  - Healthchecks: backend `/health` (60s), frontend `/nginx-health` (120s).

## Key Files

- Frontend
  - `frontend/src/utils/deepLink.ts` — deep link builders (startapp + startApp), optional short name.
  - `frontend/src/utils/telegram.ts` — `openTelegramShareLink` via `t.me/share/url`.
  - `frontend/src/components/EventDetails.tsx` — share button and message format.
  - `frontend/src/utils/format.ts` — guest count label (“+ Плюша”).

- Backend
  - `backend/app/services/telegram_links.py` — unified deep link + share text helpers.
  - `backend/app/services/event_announcement.py` — message layout, uses telegram_links, bulk delivery.
  - `backend/app/services/bot_user_broadcast.py` — broadcast to all users.
  - `backend/app/services/participant_broadcast.py` — broadcast to event registrants.
  - `backend/app/services/event_reminders.py` — 24h reminders scheduler.
  - `backend/app/bot/handlers.py` — admin FSM, “📢 Написать всем” flow, participant broadcast, create event.
  - `backend/app/main.py` — DB migration in lifespan; background tasks start after DB ready.
  - `backend/run.py` — uvicorn launcher.

- Docs
  - `docs/decisions/010-event-share-deeplink.md` — deep link formats and iOS notes.
  - `docs/decisions/011-new-event-announcement.md` — announcement details.
  - `docs/decisions/013-event-reminder-24h.md` — reminders.
  - `docs/decisions/017-bot-user-broadcast.md` — new admin broadcast to all users.
  - `docs/deploy-railway.md` — Railway setup + variables (`VITE_BOT_USERNAME`, `VITE_BOT_APP_SHORT_NAME`, etc.).

## Environment Variables (prod-relevant)

- Backend (Railway)
  - `DATABASE_URL` (Postgres), `BOT_TOKEN`, `ADMIN_TELEGRAM_IDS`, `WEBAPP_URL`, `API_BASE_URL`, `CORS_ORIGINS`
  - Optional: `BOT_APP_SHORT_NAME` (Direct Link short name for deep links in announcements)

- Frontend (Railway)
  - `API_UPSTREAM` (backend public URL, scheme optional)
  - `VITE_BOT_USERNAME=zarya_friends_bot`
  - Optional: `VITE_BOT_APP_SHORT_NAME` (Direct Link short name matching BotFather)

## Open Considerations / Notes

- Deep links on iOS are most reliable with:
  - both `startapp` and `startApp` present; and/or
  - Direct Link short name path (`/{short_name}`) configured in BotFather.
- Build times on Railway are mostly due to Docker build (pip + npm). `.dockerignore` reduces context.

## Verification Status

- Backend tests: passing (pytest)
- Frontend build: passing (Vite + TS)
