# ADR 007: Admin broadcast to event participants

## Status

Accepted

## Context

Organizers need to send situational updates (schedule changes, what to bring) to people registered for an event. Participant telegram IDs are already stored when users register via the Mini App.

## Decision

Add «Написать участникам» to the event management menu in the admin bot:

1. Admin enters message text
2. Bot shows preview with recipient count
3. Admin confirms → message sent to each recipient for that event

**Recipients (ADR-022):** users with registration status `active` **or** `maybe` (not `cancelled`). Same message body for both; one DM per user; order by `registered_at` ASC. Preview «Получателей: N» counts both.

Message format:

```
📌 {event name} · {date, time}

{admin text}
```

## Consequences

- Confirmed guests and «Подумаю» interest both get situational updates; all-bot-user broadcast (ADR-017) stays separate
- Must not reuse a widened recipient list for ADR-013 going reminders (active-only)
- Undelivered messages (blocked bot) are counted and reported to admin
- Manual flow only; no automatic send on event edit
