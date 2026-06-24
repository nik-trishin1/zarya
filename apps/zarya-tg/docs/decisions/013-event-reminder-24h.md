# ADR-013: 24-hour event reminder

**Date:** 2026-06-24
**Status:** Accepted

## Context

Registered participants should receive an automatic Telegram reminder about one day before an event starts. The message should allow quick cancellation without opening the Mini App.

## Decision

- Background scheduler in `run.py`: ticks every **60 minutes**, active **08:00–22:00 Moscow time**.
- Reminder window: event starts in **23–25 hours** from tick time (one-hour scheduler granularity).
- Track `events.reminder_sent_at` to send once per event.
- Message text:

```
Ждем вас уже завтра!
📌 {name} · {date, time}
📍 {location}
До скорой встречи! ❤️
```

- Inline button **«Не смогу прийти»** → `reminder:cancel:{event_id}` → immediate `cancel_registration()` via bot callback.

## Alternatives Considered

**30-minute scheduler.** Rejected as too frequent for MVP scale.

**24/7 scheduler ticks.** Rejected in favour of daytime-only checks; events whose exact 24h mark falls at night wait until the next 08:00 tick (still within the 23–25h window for morning events).

**Deep link to Mini App.** Rejected; inline callback is one tap.

## Consequences

- Late registrants after `reminder_sent_at` is set do not receive a reminder.
- Requires `BOT_TOKEN` and backend process running (same Railway service as API/bot).
- Zero registrants: event is still marked reminded to avoid retry loops.
