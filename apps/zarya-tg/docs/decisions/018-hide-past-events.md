# ADR-018: Hide past events (keep in database)

**Date:** 2026-07-16
**Status:** Accepted

## Context

Past events were still visible in:

- Mini App «Мои регистрации» and the ticket counter (🎫) — `/api/registrations/my` did not filter by date
- Admin bot «Управлять событиями» — `get_all_events_admin` returned every event

The home event list already showed only upcoming events (`Event.date >= today`). Keeping past events in admin/my-registrations cluttered active management and inflated the registration badge. Soft-delete / archive UI is out of MVP; Iteration 2 backlog still has a richer «Past events status» item (grey «Завершено», 48h delay, Archive).

PRD US-9 / US-11 previously said the admin list includes past and upcoming events.

## Decision

**Hide** events whose calendar date is before today from all active lists. **Do not delete** them from the database.

Surfaces affected:

1. Home event list (already filtered)
2. «Мои регистрации» and ticket counter (`get_upcoming_events(..., registered_only=True)`)
3. Admin manage list (`get_all_events_admin`)

Past-day rule stays calendar-date-only (`event.date < date.today()`), consistent with `is_event_past` / ADR tests. Rows remain queryable for future Archive or analytics.

Admin empty state copy: «Нет предстоящих событий.»

## Alternatives Considered

**Hard-delete past events.** Rejected — loses history and registration records; user asked to keep data.

**Mark as «Завершено» and keep visible.** Deferred to Iteration 2 «Past events status»; current need is hide-from-active-UI only.

**Hide after 48 hours.** Deferred — same Iteration 2 item; hide immediately after the event date for now.

## Consequences

- Admin can no longer edit/delete a past event via the bot list without a future Archive/history UI (or a one-off DB/ops action).
- Ticket counter reflects only upcoming registrations.
- Supersedes PRD US-9 / US-11 wording that required listing past events in admin.
