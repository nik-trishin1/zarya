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
   - `active` → `cancelled` unchanged; **do not** offer «Подумаю» while already going (cancel first, then maybe if needed)

3. **Capacity.** `maybe` does **not** occupy seats. Seat count remains `SUM(party_size)` over `status == active` only (ADR-012 / ADR-019). `party_size` on a maybe row is irrelevant until the user becomes `active` (then normal Один / +1 rules apply).

4. **Cascade of scheduled pings.** While status stays `maybe`, the bot sends a nudge at each **future** milestone before `event_start`. Offsets (fixed set):

   - `event_start − 7 days`
   - `event_start − 3 days`
   - `event_start − 2 days`
   - `event_start − 24 hours`

   On mark «Подумаю», **precompute and store** one schedule entry per offset whose due time is still in the future (`due_at > now`). Past offsets are skipped (e.g. mark with 5 days left → schedule 3d, 2d, 24h only).

   Ignoring a ping (no «Буду» / «Не смогу») does **not** cancel later entries — keep sending until the user leaves `maybe` or the event starts. Block marking maybe on past events; drop unsent schedule after event start.

5. **Delivery.** Same process loop pattern as ADR-013: hourly tick in `run.py`, active **08:00–22:00 Europe/Moscow**, fire when `now` is within ~±1 hour of an unsent schedule entry’s `due_at` and the registration is still `maybe`. Mark that entry sent after the attempt. Leaving `maybe` deletes or ignores remaining unsent entries. Re-marking «Подумаю» rebuilds the schedule from remaining future offsets.

6. **Ping copy and buttons (Russian).** Short nudge, e.g.:

   ```
   Вы ещё думаете про это событие?
   📌 {name} · {date, time}
   📍 {location}
   ```

   Inline keyboard: **«Буду»** → register `active` with `party_size=1` (capacity permitting; if full, stay `maybe`, keep schedule, tell the user); **«Не смогу»** → set `cancelled`. Callbacks must not open the Mini App.

   **Addendum (ADR-025):** on `requires_approval` events, **«Буду»** creates `pending`, not `active` (same 409-if-full behaviour).

7. **Relation to ADR-013.** Going reminders stay on the shared recipient helper. **Decision (2026-08-12):** `get_event_registered_users` includes `active` **and** `maybe`, so maybe users may also receive «Ждем вас уже завтра!» with «Не смогу прийти». That overlap with the maybe `−24h` cascade ping is accepted. Reminder cancel must clear `active` or `maybe`.

   The maybe cascade still uses its own schedule, copy, and **«Буду» / «Не смогу»** buttons (not `events.reminder_sent_at`).

8. **Surfaces.**

   | Surface | Include `maybe`? |
   |---|---|
   | Mini App indicator / «Подумаю» CTA | yes |
   | Cascade bot pings | yes |
   | Admin «Участники» | yes — after active seat-expanded lines, `N. Имя @username - Подумаю` (username omitted if missing); `Всего` footer = **active seats only** |
   | Participant broadcast («Написать участникам», ADR-007) | yes — same message body to `active` + `maybe`; order by `registered_at` ASC; one DM per user |
   | ADR-013 24h reminder | yes — same recipients helper as broadcast (`active` + `maybe`) |
   | «Мои регистрации» | no (active only) |
   | Calendar .ics | no (active only) |
   | Capacity / `is_full` / «Гостей» | no (active only) |
   | Admin notify on mark maybe (ADR-005) | no for v1 |

9. **Group ACL.** Treat `maybe` like `active` for “has registration on this group event” escape hatches so a maybe user who loses group membership can still open the event to confirm or clear.

10. **Capacity corner cases (deferred).** No special almost-full messaging for maybe in T-211. Future low-priority backlog: nudge maybe users when seats are nearly gone («Места почти закончились — присоединяйся»). «Буду» when full keeps existing API 409 behavior without extra product flow.

## Alternatives Considered

**Single ping only (first future tier).** Rejected — product wants continued nudges on 7d / 3d / 2d / 24h while the user remains «Подумаю».

**Window-scan only (no stored schedule).** Rejected — more logic each tick; product preferred pre-scheduling remaining milestones at mark time.

**Maybe occupies a soft hold on capacity.** Rejected — no seat reservation.

**Hide maybe from admin list / broadcasts.** Rejected — organizers need to see and message interest.

**Separate interest table.** Rejected — one RSVP row per `(user_id, event_id)` is enough.

## Consequences

- Event API needs explicit RSVP for the current user (`maybe` vs going vs none); keep `is_registered == (status == active)` so calendar and existing clients stay correct.
- Schema: `maybe` status plus a per-registration ping schedule (child rows preferred) via `create_all` + idempotent `schema_updates` as needed.
- ADR-007 recipient set expands to active + maybe (see that ADR).
- Implementation ticket: [T-211](../tickets/T-211-maybe-rsvp-delayed-ping.md).

## Addendum (ADR-025, 2026-08-18)

Fourth status `pending` (manual approval). Do not offer «Подумаю» while `pending` or `active`. Applying clears unsent maybe pings. `pending` is excluded from calendar, 24h reminders, and participant broadcasts; it **is** included in «Мои регистрации». Group ACL escape hatch treats `pending` like `maybe`. Details: [ADR-025](025-manual-registration-approval.md).
