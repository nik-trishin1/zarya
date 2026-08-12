# ADR-023: Past events archive («Архив» / «Завершено»)

**Date:** 2026-08-12
**Status:** Accepted

## Context

ADR-018 hides events with `event.date < today` from active UI (home, «Мои регистрации», ticket counter, admin manage list). Data stays in the database, but users and admins cannot browse completed history without DB access.

Iteration 2 ticket T-203 adds a read-only archive without restoring past events to the main feed.

## Decision

1. **Boundary.** Past = `event.date < date.today()` (calendar date, Europe/Moscow server date). **No 48h grace** — same rule as ADR-018.

2. **Mini App — home.** Unchanged: upcoming only.

3. **Mini App — «Мои регистрации».**
   - Top: upcoming registrations (`active` only), same as today.
   - Below: section **«Архив»** with past events where the user had **`active`** registration (going / «Был»).
   - **`maybe` is excluded** from archive.
   - Ticket counter (🎫) counts **upcoming `active` only** — unchanged from PRD / ADR-018.
   - Archive cards: muted styling + label **«Завершено»** (Russian).
   - Opening an archive event: read-only details; **no calendar export**; no register / maybe actions.

4. **API.** New `GET /api/registrations/my/archive` returning past `active` registrations for the current user (same `EventResponse` shape, `is_past: true`). Keep `GET /api/registrations/my` upcoming-only.

5. **Admin bot — archive.**
   - Separate entry **«Архив»** (or equivalent) listing past events (`date < today`), ordered by date descending.
   - From archive: **view event detail** and **«Участники»** only.
   - **No edit / delete** on archived events in T-203 (ops/DB if ever needed).
   - Past events remain addressable by `event_id` for future **T-302 duplicate** (copy fields into a new upcoming event).

6. **Deep links.** Unchanged: opening a past event by link still works; archive is an additional browse path.

## Alternatives Considered

**Include `maybe` in user archive.** Rejected — archive is for confirmed attendance history only.

**48h grace on home.** Rejected — deferred in ADR-018; product confirmed midnight boundary.

**Calendar in archive details.** Rejected for T-203 — simpler read-only UX.

**Edit/delete past events in admin archive.** Rejected — view/participants only; duplication deferred to T-302.

**Time-limited archive (e.g. 12 months).** Rejected for v1 — show all past rows.

## Consequences

- `get_upcoming_events` / `get_all_events_admin` stay upcoming-only; add parallel **past** queries for archive surfaces.
- T-302 can attach «Дублировать» to admin archive detail without schema changes (load event by id).
- Implementation: [T-203](../tickets/T-203-past-events-archive.md).
