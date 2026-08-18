# ADR-025: Manual registration approval («по заявке»)

**Date:** 2026-08-18  
**Status:** Proposed (implementation waits on spec/ticket Human summary approve)

## Context

Some events should not auto-confirm attendance. Organizers need a gate after a user taps register — to screen who comes, and/or to wait for an off-platform payment — before the person appears as going.

Today RSVP is `active` / `maybe` / `cancelled` (ADR-022). Registering immediately sets `active`, occupies seats (ADR-012 / ADR-019), unlocks calendar, and can trigger 24h reminders (ADR-013). Kicking people afterwards is too late: they already saw «Иду».

This is an **opt-in per event**, not a new audience and not in-app payments. Price display is separate ([ADR-026](026-event-price.md)).

## Decision

### 1. Event flag

Add `events.requires_approval` (`BOOLEAN NOT NULL DEFAULT FALSE`).

- **Off (default):** POST register → `active`, same as today.
- **On:** POST register (and maybe-ping «Буду») → `pending`.
- Set in the admin **create** FSM after capacity: **«Запись сразу»** / **«По заявке»**.
- **Not editable after create** in v1 (same constraint as capacity). Existing events stay open registration.

### 2. Registration status `pending`

Keep one row per `(user_id, event_id)`. Extend `registrations.status` with `pending`.

Transitions:

- none / `cancelled` / `maybe` → `pending` (apply on an approval event)
- `pending` → `active` (admin **Принять**, capacity permitting)
- `pending` → `cancelled` (admin **Отклонить**, or user **Отменить заявку**)
- `cancelled` → `pending` on re-apply — **always a new review**, even if previously approved
- `active` → `cancelled` unchanged
- While `pending` or `active`, do **not** offer «Подумаю»

`party_size` is stored on the application (1 or 2) at apply time. PATCH party_size remains **active-only**; to change +1 while pending, cancel and apply again.

### 3. Capacity

`pending` does **not** occupy seats. Seat count stays `SUM(party_size)` over `status == active` only.

- Apply when the event is already full → **409** / «Мест нет» (waitlist is out of scope).
- Approve checks `reg_count + party_size ≤ max_participants`. If not enough seats: tell the admin, leave status `pending`.
- Approve of a `party_size=2` row is all-or-nothing.

### 4. Surfaces

| Surface | Include `pending`? |
|---|---|
| Mini App badge / apply CTA | yes — **«На рассмотрении»**; CTA **«Записаться»** (not «Буду») |
| «Мои регистрации» (upcoming) | yes — so the user can withdraw the application |
| Calendar | no (`is_registered` stays **active-only**) |
| ADR-013 24h reminder | no |
| Maybe cascade pings | no while `pending` (clear unsent maybe pings on apply) |
| Participant broadcast (ADR-007) | no in v1 |
| Admin «Участники» (ADR-006) | yes — separate **Заявки** block with **Принять** / **Отклонить** |
| Capacity / `is_full` / «Гостей» | no (active only) |
| Admin notify (ADR-005) | yes — application DM with buttons (not «будет на») |
| Group-event ACL escape hatch | yes — treat like `maybe` / `active` so the applicant can still open the event |

API: keep `is_registered == (status == active)`. Add `is_pending` (true only when status is `pending`). Expose `requires_approval` on event responses.

### 5. Admin decision in the bot

On apply, DM every `ADMIN_TELEGRAM_IDS` (same delivery rules as ADR-005: failures logged, API not blocked):

```
{mention} подал(а) заявку на *{name}* *{date}*
Гостей в заявке: 1
Всего гостей: {active_seats}

[Принять] [Отклонить]
```

(Use `Гостей в заявке: 2` when `party_size=2`.)

The same two buttons appear on each pending line under event **Участники**, in case the DM is missed.

**Accept** → `active`; user DM:

```
Ваше участие на {name} · {date, time} подтверждено!
```

**Reject** → `cancelled`; user DM:

```
Заявку на {name} не подтвердили.
```

No reject reason in v1. Callbacks are idempotent: if the row is no longer `pending`, tell the admin and do not re-notify the user.

User cancel of a pending row uses the existing cancel-notify wording (application withdrawn), **without** accept/reject buttons.

### 6. Maybe RSVP on approval events

«Подумаю» stays available when the user is not `pending` or `active`. Maybe ping **«Буду»** on `requires_approval` events creates `pending`, not `active`. If the event is full, keep existing 409 behaviour (stay `maybe`).

### 7. Open events

Unchanged: register → `active`; ADR-005 «будет на» / cancel copy; no decision buttons.

## Alternatives considered

**Admin deletes unwanted `active` rows after the fact.** Rejected — calendar, «Иду», and 24h reminders fire before the gate.

**Pending occupies a seat until reject.** Rejected — unpaid / unreviewed applications would block a paid event.

**In-app payments.** Rejected — out of scope (PRD; ADR-026 is display-only). Approval is the human gate after an off-platform transfer.

**Always-on approval for every event.** Rejected — would kill two-tap RSVP on ordinary friend gatherings. Default off.

**Auto-approve remaining pending if the admin turns the flag off.** Rejected — flag is create-only in v1.

## Consequences

- Fourth RSVP status; all `active`-only helpers (capacity, calendar, `is_registered`) must ignore `pending`.
- «Мои регистрации» / ticket badge must include upcoming `pending` as well as `active` (distinct badge).
- ADR-005, ADR-006, ADR-007, ADR-013, ADR-022: see addenda on those files.
- Spec: [S-213](../specs/S-213-manual-registration-approval.md). Tickets: [T-213](../tickets/T-213-approval-backend-bot.md), [T-214](../tickets/T-214-approval-mini-app.md).
