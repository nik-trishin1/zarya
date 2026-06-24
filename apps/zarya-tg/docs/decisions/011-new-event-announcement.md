# ADR-011: New event announcement to all bot users

**Date:** 2026-06-23
**Status:** Accepted

## Context

When an admin creates an event, the community should optionally receive a Telegram announcement with event details and a deep link to open the Mini App on that event.

Bulk delivery infrastructure already exists: `deliver_bot_message`, `deliver_bot_messages_to_users`, and `bot_blocked_at` tracking (ADR 009).

## Decision

On the event creation confirmation screen, the admin chooses:

- **🔔 Создать и уведомить всех** — create the event and broadcast an announcement to every user in the `users` table
- **✅ Создать без уведомления** — create only (previous behaviour)

Announcement format:

```
🌅 Новое событие!

📌 {name} · {date, time}
📍 {location}

{description if present}

{name}
https://t.me/{bot_username}?startapp=event_{id}
```

The confirmation screen shows how many users are registered in the bot. After send, the admin sees delivery stats (sent / blocked / failed), same as participant broadcast.

Recipients are all users who have ever `/start`ed the bot or opened the Mini App — not only event registrants.

## Alternatives Considered

**Separate post-create prompt.** Extra step after creation; rejected in favour of a single confirmation choice.

**Notify only users who opened the Mini App recently.** Requires extra tracking; out of scope for MVP.

## Consequences

- Large user bases may take several seconds to fan out; acceptable for ~20-user MVP.
- Users who blocked the bot are counted in `blocked`; delivery is skipped on retry until they unblock.
- Bot username is resolved via `get_me()` at send time; no new env var required.
