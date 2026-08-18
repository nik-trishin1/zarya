# S-213 — Manual registration approval («по заявке»)

## Human summary (review this first)

**In plain language, we will:**
- Let the admin mark an event as «по заявке» when creating it (ordinary events stay one-tap «Буду»)
- When a guest taps «Записаться», they wait for confirmation instead of immediately counting as going
- The admin accepts or declines each application in the Telegram bot (notification buttons and the event’s participant list)
- If the guest cancels and applies again, the admin reviews them again — even if they were accepted before
- Confirmed guests then use the same cancel, calendar, +1, and reminders as today

**We will not:**
- Charge money in the app (price on the card is a separate spec; payment stays outside)
- Hold a seat for an unconfirmed application
- Let the admin change «по заявке» after the event exists
- Ask for a decline reason, auto-expire applications, or build a waitlist
- Message unconfirmed applicants with «Написать участникам» or the «tomorrow» reminder

**User-visible outcome:**
- Paid or selective events: apply → «На рассмотрении» → bot «Принять» / «Отклонить» → guest gets a confirmation or a polite no. Friend hangs stay as they are.

**Main risks / open questions already decided:**
- `pending` does not occupy capacity; approve checks seats (ADR-025)
- Re-apply after cancel/reject always goes back to pending
- «Подумаю» still exists on approval events until the user applies or is going
- Calendar and 24h reminder only after accept
- `is_registered` stays active-only; new `is_pending`

**How we will know it worked (smoke):**
- Create «по заявке» → Mini App «Записаться» → badge «На рассмотрении» → guest count unchanged → event appears under «Мои»
- Admin «Принять» → guest DM «Ваше участие на {name} · {date, time} подтверждено!» → «Иду», calendar, guest count +1
- Admin «Отклонить» → guest DM «Заявку на {name} не подтвердили.» → can apply again (pending again)
- Cancel then apply again → new admin decision DM
- Ordinary event (flag off) still registers as «Иду» immediately

**Reviewer decision:** `[ ] Approved for ticket split` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-213 |
| Title | Manual registration approval («по заявке») |
| Status | `draft` |
| Related ADR / PRD | [ADR-025](../decisions/025-manual-registration-approval.md); [ADR-005](../decisions/005-admin-registration-notifications.md); [ADR-006](../decisions/006-admin-participant-list.md); [ADR-007](../decisions/007-participant-broadcast.md); [ADR-012](../decisions/012-event-capacity-limit.md); [ADR-013](../decisions/013-event-reminder-24h.md); [ADR-019](../decisions/019-registration-party-size.md); [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md). Price is [S-215](S-215-event-price.md) / [ADR-026](../decisions/026-event-price.md). |
| Owner | zarya maintainers |

## Problem

Some events (festivals, paid trips) need a human gate after «I want to come» and before «you are going». Instant `active` RSVP is too early: seats, calendar, and reminders treat the person as confirmed.

## Goals

- Per-event opt-in approval (`requires_approval`, default false)
- `pending` RSVP with admin accept/reject in the bot
- Distinct Mini App copy and «Мои регистрации» for applications
- Re-apply always re-enters review
- Leave open events and `maybe` behaviour intact except the ping «Буду» path on approval events

## Non-goals

- Payments / «оплачено»
- Pending occupying seats
- Editing `requires_approval` after create
- Reject reason, application deadline, auto-reject
- Waitlist when full
- Broadcast or 24h reminder to `pending`
- Public participant list

## Proposed behavior

### Data / API

- `events.requires_approval BOOLEAN NOT NULL DEFAULT FALSE` via model + `schema_updates`.
- `registrations.status` includes `pending` (`RegistrationStatus`).
- `EventResponse`: `requires_approval`, `is_pending` (true only if current user status is `pending`; mutually exclusive with `is_registered` / `is_maybe`).
- `is_registered` remains `status == active`.
- `registration_count` / `is_full`: `SUM(party_size)` over **active** only.
- `POST /registrations/{event_id}`:
  - open event: `active` (today)
  - `requires_approval`: `pending` (from none / cancelled / maybe); 409 if already active or already pending; 409 if full; 410 if past
- `POST /registrations/{event_id}/maybe`: 409 if pending or active (same as already going)
- `PATCH` party_size: **active only** (422/409 if pending)
- `DELETE`: pending or active or maybe → `cancelled`; pending cancel does not decrement seats
- `GET /registrations/my`: upcoming events where status is `active` **or** `pending`
- New admin-only service (bot callbacks, not Mini App): `approve_registration(event_id, user_id)` / `reject_registration(...)`.
- Group ACL: `pending` counts as “has a registration” for the same escape hatch as `maybe`.
- Applying clears unsent maybe pings.

### UI / bot copy (user-facing language)

**Mini App**

- Approval event, not going / not pending: circle caption **«Записаться»** (going circle still used; +1 chip allowed at apply)
- After apply: badge **«На рассмотрении»**; ghost **«Отменить заявку»**; no calendar; no «Подумаю»; +1 chip hidden until accepted
- After accept: same as today (**«Буду»** selected / **«Иду»**, **«Отменить регистрацию»**, calendar, +1)
- Toast on apply: **«Заявка отправлена. Ждём подтверждения.»**
- List card overlay for pending: **«На рассмотрении»** (not «Иду» / «Подумаю»)
- Full + not pending: **«Мест нет»** (cannot apply)

**Admin create**

- After capacity: **«Как записывать?»** — **«Запись сразу»** / **«По заявке»**
- Confirm preview includes the mode

**Admin DMs and list**

- Application:

  ```
  {mention} подал(а) заявку на *{name}* *{date}*
  Гостей в заявке: {party_size}
  Всего гостей: {active_seats}
  ```

  Buttons: **Принять** · **Отклонить**

- Accept → user: **«Ваше участие на {name} · {date, time} подтверждено!»**
- Reject → user: **«Заявку на {name} не подтвердили.»**
- «Участники»: block **Заявки** first, then active seats, then maybe. Pending line: `N. Имя @username — на рассмотрении` + the same two buttons. `Всего` = active seats.

**Maybe ping** on approval events: **«Буду»** → pending (user should see that they applied, not that they are going). Short confirmation in the callback alert/message, e.g. заявка отправлена.

### Errors and edge cases

- Approve when full → bot tells admin «Недостаточно мест»; status stays `pending`
- Double-tap Принять after already active → «Уже подтверждено»; no second user DM
- Double-tap Отклонить after cancelled → «Заявка уже снята»; no second user DM
- User cancelled while admin taps Принять → treat as no longer pending
- Past events: no new applications; pending rows may remain but Mini App is past-locked as today
- `party_size=2` approve needs two free seats
- Open event: no pending path; ADR-005 «будет на» unchanged

## Acceptance criteria (spec-level)

- [ ] Flag default false; create-only; existing events stay open registration
- [ ] Apply → `pending`, seats unchanged, `is_pending`, appears in «Мои», calendar hidden
- [ ] Accept → `active`, seats increase, user DM exact accept copy, calendar available
- [ ] Reject → `cancelled`, user DM exact reject copy, can apply again as `pending`
- [ ] Cancel + re-apply → new admin decision message
- [ ] Full event: cannot apply (409); approve of leftover pending fails if now full
- [ ] Maybe ping «Буду» on approval event → `pending`
- [ ] Broadcast and 24h reminder exclude `pending`
- [ ] Open events unchanged
- [ ] Backend tests for transitions/capacity/recipients; Mini App covered in T-214

## Rollout / migration

- `schema_updates` add `requires_approval` default false
- No backfill; no change to existing RSVP rows
- Ship T-213 (API + bot) before or with T-214 (Mini App). Old clients without `is_pending` would still POST register and land in pending — they need T-214 copy to make sense. Prefer same release train.

## Open questions

> Deferred (not blocking): dedicated «написать заявителям» broadcast; editing `requires_approval` after create; reject reason.

---

**Tickets:** [T-213](../tickets/T-213-approval-backend-bot.md) backend + bot · [T-214](../tickets/T-214-approval-mini-app.md) Mini App
