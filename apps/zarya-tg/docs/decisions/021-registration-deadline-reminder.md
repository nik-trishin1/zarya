# ADR-021: Soft registration deadline + day-before reminder

**Date:** 2026-07-27
**Status:** Accepted (product chat)

## Context

For some events the organizer wants a **registration deadline date** and a nudge to people who still have not registered. Product choices (2026-07-27):

1. **Soft deadline** — after the date, registration and cancellation stay allowed; the deadline is informational + reminder only (not a hard gate).
2. **Optional calendar date** — admin may leave empty (= no deadline, no reminder). When set, the deadline is **end of that day Europe/Moscow** (whole calendar day inclusive).

Audience for the nudge must match event visibility:

- Public event (`audience_group_id` null) → all bot users who are **not** actively registered.
- Group event → members of that group who are **not** actively registered.

An in-process hourly scheduler already exists for the 24h *event-start* reminder (ADR-013). Access-group recipient helpers already exist (ADR-020 / `get_announcement_recipients`).

## Decision

### Schema

- `events.registration_deadline_date` — `Date`, nullable. `NULL` = no deadline.
- `events.registration_deadline_reminder_sent_at` — `DateTime(tz=True)`, nullable. Set once when the deadline reminder fan-out runs (or is skipped as empty/no-op for that event).

No hard-block column or registration API change beyond exposing the date for UI.

### Semantics

| Concept | Rule |
|---------|------|
| Deadline instant | End of `registration_deadline_date` in `Europe/Moscow` (informational; not used to reject register/cancel) |
| Inclusive wording | Users may still register on the deadline day; copy says «до {date} включительно» |
| Validation on create/edit | If set: `registration_deadline_date` must be **≥ today (MSK)** at save time and **≤ `event.date`**. Clearing to `NULL` is allowed on edit |
| Soft after date | Register / cancel / party_size PATCH unchanged; Mini App may show that the deadline day has passed but **must not** disable registration for that reason alone |

### Reminder scheduler

Extend the same backend process loop as ADR-013 (hourly ticks, active **08:00–22:00 MSK**). Do **not** use a 23–25h window relative to 23:59 — that would land mostly outside active hours.

**When to send (once per event):**

- `registration_deadline_date IS NOT NULL`
- `registration_deadline_reminder_sent_at IS NULL`
- Moscow calendar date is **exactly one day before** the deadline: `today_msk + 1 day == registration_deadline_date`
- Scheduler is in an active hour

**Recipients:** `get_announcement_recipients(db, event.audience_group_id)` minus users with an **active** registration for that event (one DM per user). Delivery via `deliver_bot_message` / existing fan-out helpers; respect `bot_blocked_at` (ADR-009).

**Idempotency:** always set `registration_deadline_reminder_sent_at` after the attempt, including when the eligible list is empty, so the event is not retried every hour.

**Missed window:** if the event is created after 22:00 on the day before the deadline, or the process was down that day, no catch-up on the deadline day in v1 (same class of edge case as ADR-013 night misses). Documented; no second reminder day.

This reminder is **independent** of `reminder_sent_at` (event-start reminder to *registered* users). An event may trigger both on different days.

### Message (Russian)

```
Скоро закрывается регистрация!

📌 {name} · {event date, time}
📅 Регистрация до {deadline date} включительно
📍 {location}

Зарегистрироваться:
https://t.me/{bot_username}?startapp=event_{id}&startApp=event_{id}
```

(Use the same deep-link pattern as ADR-011 / ADR-010. No inline cancel button — recipients are not registered.)

### Admin bot

- Create FSM: optional step after audience (or capacity) — ask for deadline date (`DD.MM.YYYY`) or «Без дедлайна».
- Edit: allow set / change / clear deadline (unlike create-only capacity in ADR-012).
- Confirm / manage detail: show deadline or «без дедлайна».

### Mini App / API

- Expose `registration_deadline_date: string | null` (ISO date) on event payloads.
- Optional computed `is_registration_deadline_passed` (MSK calendar: `today > registration_deadline_date`) for copy only.
- Event details: if deadline set, show «Регистрация до {date} включительно»; if passed, softer line that the suggested deadline has passed — **button still works** (capacity / past event rules unchanged).

## Alternatives considered

**Hard close after deadline.** Rejected by product — soft only for this iteration.

**Date+time deadline.** Rejected — date-only is enough; end-of-day MSK is the implicit cutoff for messaging.

**Relative “N hours before event start”.** Rejected — organizers think in calendar days.

**Reuse 23–25h window vs end-of-day.** Rejected — conflicts with daytime-only scheduler.

**Remind on deadline morning as catch-up.** Deferred — keep one clear “day before” rule.

## Consequences

- New schema columns + create/edit FSM + scheduler branch + tests.
- Users who register after the reminder still receive the later ADR-013 start reminder if applicable.
- Users who join a group after the deadline reminder was sent do not get a retroactive DM.
- Soft deadline can be ignored by users; organizers who need a hard cutoff need a future ADR.
