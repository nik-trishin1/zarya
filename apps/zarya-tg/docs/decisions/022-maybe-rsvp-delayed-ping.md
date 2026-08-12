# ADR-022: Maybe RSVP («Подумаю») + delayed bot ping

**Date:** 2026-08-12
**Status:** Accepted (product rules locked; implementation waits on T-211 Human summary approve)

## Context

Users often are not ready to confirm attendance when they open an event. Today RSVP is binary (`active` / `cancelled`). A third state — «Подумаю» — lets them bookmark interest without taking a seat, and the bot should nudge them later so the decision does not get lost.

Existing 24h reminders (ADR-013) only target **active** registrants, once per event via `events.reminder_sent_at`. That model cannot schedule per-user maybe follow-ups.

## Decision

1. **Status.** Extend `registrations.status` with `maybe` alongside `active` and `cancelled`. Keep one row per `(user_id, event_id)`. Mini App primary label: **«Подумаю»**.

2. **Transitions.**
   - Not registered / cancelled → `maybe` (tap «Подумаю»)
   - `maybe` → `active` (Mini App «Буду» / «Буду +1», or bot ping «Буду»)
   - `maybe` → `cancelled` (Mini App cancel / clear, or bot ping «Не смогу»)
   - `active` → `cancelled` unchanged; user may set `maybe` again later from a non-active state

3. **Capacity.** `maybe` does **not** occupy seats. Seat count remains `SUM(party_size)` over `status == active` only (ADR-012 / ADR-019). `party_size` on a maybe row is irrelevant until the user becomes `active` (then normal Один / +1 rules apply).

4. **Precompute one ping.** When status becomes `maybe`, set `registrations.maybe_ping_at` from the tier table below and clear `registrations.maybe_ping_sent_at`. The scheduler only selects due maybe rows — no continuous “is it 7 days before?” scans across all events.

   | Time until `event_start` at mark | `maybe_ping_at` |
   |---|---|
   | ≥ 8 days | `event_start − 7 days` |
   | ≥ 4 and &lt; 8 days | `event_start − 3 days` |
   | ≥ 3 and &lt; 4 days | `event_start − 2 days` |
   | &lt; 3 days | `event_start − 24 hours` |

5. **Delivery.** Same process loop pattern as ADR-013: hourly tick in `run.py`, active **08:00–22:00 Europe/Moscow**, fire when `now` is within ~±1 hour of `maybe_ping_at` and `maybe_ping_sent_at IS NULL` and status is still `maybe`. After the send attempt, set `maybe_ping_sent_at` so there is **no retry / no second ping** until the user marks «Подумаю» again.

6. **Ping copy and buttons (Russian).** Short nudge, e.g.:

   ```
   Вы ещё думаете про это событие?
   📌 {name} · {date, time}
   📍 {location}
   ```

   Inline keyboard: **«Буду»** → register `active` with `party_size=1` (capacity permitting); **«Не смогу»** → set `cancelled` (or equivalent clear of maybe). Callbacks must not open the Mini App.

7. **Relation to ADR-013.** Unchanged for `active` users. Maybe users never receive the going reminder. The &lt;3-day tier uses a **maybe-specific** ~24h ping (different copy/buttons), not `events.reminder_sent_at`.

8. **Surfaces.**
   - Event details / cards: show a distinct maybe indicator (not the going ✅).
   - «Мои регистрации», calendar export, capacity, participant broadcast, admin guest list: **active only** (maybe is not a guest).

## Alternatives Considered

**Window-scan only (no `maybe_ping_at`).** Rejected — more logic each tick and harder to reason about missed windows; product preferred pre-scheduling.

**Cascade of 7d + 3d + 2d + 24h for every maybe.** Rejected for v1 — one ping per maybe cycle is enough; repeated nags are out of scope.

**Maybe occupies a soft hold on capacity.** Rejected — product wants no seat reservation.

**Separate interest table.** Rejected — `UniqueConstraint(user_id, event_id)` already models one RSVP row; a third status is simpler.

## Consequences

- All `status == active` filters (capacity, my list, reminders, broadcasts, admin list) must stay active-only; new code paths must not treat maybe as registered for seats.
- Event API needs an explicit RSVP signal for the current user (`maybe` vs going vs none), not only `is_registered: bool`.
- Schema updates add `maybe` status usage plus `maybe_ping_at` / `maybe_ping_sent_at` on `registrations` (idempotent `schema_updates`, same as other Iteration 2 columns).
- Implementation ticket: [T-211](../tickets/T-211-maybe-rsvp-delayed-ping.md).
