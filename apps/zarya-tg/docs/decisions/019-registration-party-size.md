# ADR-019: Registration party size (+1)

**Date:** 2026-07-24
**Status:** Accepted

## Context

Participants often bring one unidentified guest. Capacity (ADR-012) counts physical seats, so a "+1" must occupy two seats when a limit exists. Identifying the second person is not required and stays out of scope (privacy / MVP).

Current schema enforces one registration row per `(user_id, event_id)`. Seat count used `COUNT(registrations)`.

## Decision

1. Add `registrations.party_size` (integer, default `1`, minimum `1`). MVP UI and API accept only `1` or `2`; the column is intentionally open-ended for a future "N tickets per guest" without a schema redesign.
2. **Seat occupancy** for capacity and "Гостей: X из Y" is `SUM(party_size)` over active registrations (not row count).
3. Register with `party_size` in the POST body. After registration, PATCH may change `party_size` (add/remove +1).
4. Increasing `party_size` requires enough free seats (`max_participants - SUM(party_size)`). If only one seat remains, "+1" is unavailable (muted / rejected with 409).
5. Cancelling registration cancels the whole row (all seats for that user).
6. Admin participant list (ADR-006) expands each registration into `party_size` numbered lines so the list length matches guest count, e.g.:
   - `1. Никита @nick`
   - `2. Никита + 1`
   - `3. Другой гость @other`
7. Broadcasts and 24h reminders still target unique registered users once (not once per seat).

## Alternatives Considered

**Two registration rows per user.** Rejected — breaks `UniqueConstraint(user_id, event_id)` and complicates cancel / "my registrations" without benefit when the guest is anonymous.

**Separate `guests` table with names.** Rejected for MVP — user explicitly does not need to identify +1.

## Consequences

- All capacity checks and guest counters must use `SUM(party_size)`.
- Event API exposes the current user's `party_size` (0 / omitted when not registered) so the Mini App can show add/remove +1.
- ADR-006 list formatting becomes seat-expanded; total line equals seats.
- Raising the MVP max above 2 later is mostly validation + UI, not a migration.
