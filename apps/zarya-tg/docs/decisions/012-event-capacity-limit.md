# ADR-012: Event capacity limit

**Date:** 2026-06-23
**Status:** Accepted

## Context

Some events have a physical capacity. Admins need to cap registrations; participants should see occupancy and cannot register when the event is full.

## Decision

- Add nullable `events.max_participants` (`NULL` = unlimited).
- During admin event creation, after description, admin enters a number or chooses **«Без лимита»**.
- API responses include `max_participants`, `is_full` (when `registration_count >= max_participants`).
- Registration endpoint rejects new sign-ups when full (HTTP 409).
- Mini App UI:
  - With limit: **«Гостей: X из Y»**
  - Without limit: **«Гостей: N»**
  - Full + not registered: **«Fully booked. Stay tuned!»** and disabled register button (same pattern as past events).

## Consequences

- Capacity is not editable in the admin edit flow yet (create-only for MVP).
- Race at exact capacity may allow slight overrun without DB-level locking; acceptable for ~20-user MVP.
- Cancelled registrations free a seat immediately.
