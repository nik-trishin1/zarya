# zarya-tg backend

FastAPI + aiogram Telegram Mini App API and bot. Local: see app `scripts/dev-local.sh` or `python run.py` with `backend/.env`.

## Module map

| Path | Role |
|------|------|
| `app/main.py` | FastAPI app, lifespan, router mount |
| `app/config.py` | Settings / env |
| `app/database.py` | Async SQLAlchemy engine + sessions |
| `app/schema_updates.py` | Startup schema patches (no Alembic yet) |
| `app/api/` | REST: events, registrations, health auth |
| `app/bot/handlers/` | Aiogram routers by flow (admin, create/edit, approvals, reminders, broadcast) |
| `app/bot/keyboards.py` | Inline / reply keyboards |
| `app/bot/states.py` | FSM states |
| `app/models/` | SQLAlchemy models |
| `app/schemas/` | Pydantic request/response models |
| `app/services/events/` | Event queries, mutations, attendance serialization |
| `app/services/access_groups.py` | Audience groups + ACL |
| `app/services/telegram_delivery.py` | Send + blocked-user tracking; shared broadcast send |
| `app/services/participant_broadcast.py` | Per-event participant broadcast copy + send |
| `app/services/bot_user_broadcast.py` | All-users broadcast copy + send |
| `app/services/event_announcement.py` | New-event announcement |
| `app/services/event_reminders.py` | 24h reminders |
| `app/services/maybe_pings.py` | «Подумаю» delayed pings |
| `app/services/admin_notifications.py` | Admin registration notifications |
| `app/services/users.py` | User upsert on `/start` |
| `app/services/storage.py` | Cover image storage helpers |
| `app/utils/` | Formatting, pricing, calendar, auth helpers |
| `tests/` | Pytest suite |

## Scripts

```bash
pip install -r requirements.txt
pytest
```
