# ADR-022: Maybe RSVP («Подумаю») + delayed bot ping

**Date:** 2026-08-12
**Status:** Accepted

## Context

Users often are not ready to confirm attendance when they open an event. Today RSVP is binary (`active` / `cancelled`). A third state — «Подумаю» — lets them bookmark interest without taking a seat, and the bot should nudge them on the way to the event so the decision does not get lost.

Existing 24h reminders (ADR-013) only target **active** registrants, once per event via `events.reminder_sent_at`. That model cannot schedule per-user maybe follow-ups.

## Decision

1. **Status.** Extend `registrations.status` with `maybe` alongside `active` and `cancelled`. Keep one row per `(user_id, event_id)`. Mini App primary label: **«Подумаю»**.

2. **Transitions.**
   - Not registered / cancelled → `maybe` (tap «Подумаю»)
   - `maybe` → `active` (Mini App «Буду» / «Буду +1», or bot ping «Буду»)
   - `maybe` → `cancelled` (Mini App cancel / clear, or bot ping «Не смогу»)
   - `active` → `cancelled` unchanged; user may set `maybe` again later from a non-active state

3. **Capacity.** `maybe` does **not** occupy seats. Seat count remains `SUM(party_size)` over `status == active` only (ADR-012 / ADR-019). `party_size` on a maybe row is irrelevant until the user becomes `active` (then normal Один / +1 rules apply).

4. **Cascade of scheduled pings.** While status stays `maybe`, the bot sends a nudge at each **future** milestone before `event_start`. Offsets (fixed set):

   - `event_start − 7 days`
   - `event_start − 3 days`
   - `event_start − 2 days`
   - `event_start − 24 hours`

   On mark «Подумаю», **precompute and store** one schedule entry per offset whose due time is still in the future (`due_at > now`). Past offsets are skipped (e.g. mark with 5 days left → schedule 3d, 2d, 24h only).

   Ignoring a ping (no «Буду» / «Не смогу») does **not** cancel later entries — keep sending until the user leaves `maybe` or the event starts.

5. **Delivery.** Same process loop pattern as ADR-013: hourly tick in `run.py`, active **08:00–22:00 Europe/Moscow**, fire when `now` is within ~±1 hour of an unsent schedule entry’s `due_at` and the registration is still `maybe`. Mark that entry sent after the attempt. Leaving `maybe` deletes or ignores remaining unsent entries. Re-marking «Подумаю» rebuilds the schedule from remaining future offsets.

6. **Ping copy and buttons (Russian).** Short nudge, e.g.:

   ```
   Вы ещё думаете про это событие?
   📌 {name} · {date, time}
   📍 {location}
   ```

   Inline keyboard: **«Буду»** → register `active` with `party_size=1` (capacity permitting); **«Не смогу»** → set `cancelled` (or equivalent clear of maybe). Callbacks must not open the Mini App.

7. **Relation to ADR-013.** Unchanged for `active` users. Maybe users never receive the going reminder. The maybe `−24h` entry is a **maybe-specific** ping (different copy/buttons), not `events.reminder_sent_at`.

8. **Surfaces.**
   - Event details / cards: show a distinct maybe indicator (not the going ✅).
   - Admin «Участники» (ADR-006 / ADR-019): include maybe rows **after** active seat-expanded lines, labeled like `Имя - Подумаю` (username rules unchanged). Maybe lines do **not** count toward capacity / «Гостей: X из Y».
   - «Мои регистрации», calendar export, participant broadcast: **active only**.

## Alternatives Considered

**Single ping only (first future tier).** Rejected — product wants continued nudges on 7d / 3d / 2d / 24h while the user remains «Подумаю».

**Window-scan only (no stored schedule).** Rejected — more logic each tick and harder to reason about missed windows; product preferred pre-scheduling all remaining milestones at mark time.

**Maybe occupies a soft hold on capacity.** Rejected — product wants no seat reservation.

**Separate interest table.** Rejected — `UniqueConstraint(user_id, event_id)` already models one RSVP row; a third status is simpler.

**Hide maybe from admin guest list.** Rejected — organizers need to see interest; label distinguishes them from confirmed guests.

## Consequences

- Capacity, «Мои регистрации», .ics, ADR-013, and participant broadcasts stay **active-only**; admin list is the exception for visibility.
- Event API needs an explicit RSVP signal for the current user (`maybe` vs going vs none), not only `is_registered: bool`.
- Schema: `maybe` status plus a per-registration ping schedule (child rows or equivalent JSON entries with `due_at` / `sent_at` / offset id) via idempotent `schema_updates`.
- Implementation ticket: [T-211](../tickets/T-211-maybe-rsvp-delayed-ping.md).
