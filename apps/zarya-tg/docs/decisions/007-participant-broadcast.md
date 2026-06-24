# ADR 007: Admin broadcast to event participants

## Status

Accepted

## Context

Organizers need to send situational updates (schedule changes, what to bring) to people registered for an event. Participant telegram IDs are already stored when users register via the Mini App.

## Decision

Add «Написать участникам» to the event management menu in the admin bot:

1. Admin enters message text
2. Bot shows preview with recipient count
3. Admin confirms → message sent to each active registrant

Message format:

```
📌 {event name} · {date, time}

{admin text}
```

## Consequences

- Only registered participants receive the message (not all bot users)
- Undelivered messages (blocked bot) are counted and reported to admin
- Manual flow only; no automatic send on event edit
