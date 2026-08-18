# T-213 — Backend + bot: registration approval


## Human summary (review this first)

**Will do:**
- Add event flag «по заявке» (`requires_approval`) and RSVP status `pending`
- Applying on those events does not take a seat; admin accepts or declines in the bot (DM buttons + participant list)
- Notify the guest on the decision; re-apply after cancel always returns to pending
- Maybe-ping «Буду» on approval events creates a pending application

**Will not do:**
- Mini App UI/copy (T-214)
- Payments or price fields (T-215)
- Occupying seats while pending, waitlists, reject reasons, editing the flag after create
- Broadcasting or 24h reminders to pending applicants

**Touched areas:** registrations model/API, event flag, admin create FSM, admin DMs and «Участники», maybe-ping callback, my-registrations query

**Risk:** Medium — easy to leak `pending` into capacity, calendar helpers, broadcasts, or treat re-apply as already approved

**Smoke check after merge:** Create approval event → POST register → `is_pending`, seats unchanged → admin Принять → `active` + user DM exact copy; Отклонить then POST again → pending again; open event still goes `active` immediately

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____  
**DoR:** `[ ] Not ready` — Human summary + S-213 must be approved first

---

| Field | Value |
|-------|-------|
| ID | T-213 |
| Title | Backend + bot registration approval |
| Status | `todo` |
| Spec / ADR | [S-213](../specs/S-213-manual-registration-approval.md), [ADR-025](../decisions/025-manual-registration-approval.md); ADR-005/006/007/012/013/019/022 addenda |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Persist approval-mode events and pending applications; let admins decide in the bot; keep `active`-only semantics for seats, calendar, reminders, and broadcasts.

## Acceptance criteria

- [ ] `events.requires_approval` default false via model + `schema_updates`; create FSM after capacity: «Запись сразу» / «По заявке»; not on edit
- [ ] `registrations.status` supports `pending`; one row per `(user_id, event_id)`
- [ ] POST register on approval event → `pending` from none/cancelled/maybe; 409 if already pending/active, full, or past; seats / `is_full` unchanged
- [ ] `EventResponse` / registration response: `requires_approval`, `is_pending`; `is_registered` still active-only
- [ ] `GET /registrations/my` includes upcoming `pending` as well as `active`
- [ ] Apply clears unsent maybe pings; PATCH party_size remains active-only
- [ ] Admin application DM with **Принять** / **Отклонить**; same buttons in «Участники» Заявки block; `Всего` = active seats
- [ ] Accept → `active` if seats allow, else stay pending and tell admin; user DM `Ваше участие на {name} · {date, time} подтверждено!`
- [ ] Reject → `cancelled`; user DM `Заявку на {name} не подтвердили.`
- [ ] Callbacks idempotent (no duplicate user DMs)
- [ ] User cancel of pending uses cancel-notify **without** decision buttons
- [ ] Re-apply after cancel/reject → `pending` + new admin DM (does not restore prior approval)
- [ ] Maybe ping «Буду» on `requires_approval` → `pending` (`party_size=1`); 409 if full keeps `maybe`
- [ ] ADR-007 broadcast and ADR-013 reminder helpers exclude `pending`
- [ ] Group ACL escape hatch treats pending like maybe
- [ ] Open events: register still `active`; ADR-005 «будет на» unchanged
- [ ] Backend tests for the transitions above; no Mini App changes in this ticket

## Out of scope

- T-214 Mini App
- T-215 price
- Waitlist, reject reason, editing `requires_approval`
- Pending in calendar / 24h reminder / participant broadcast

## Implementation notes (for agents)

- Key files: `backend/app/models/event.py`, `models/registration.py`, `schema_updates.py`, `schemas/event.py`, `schemas/registration.py`, `services/events.py`, `utils/formatting.py`, `api/registrations.py`, `services/admin_notifications.py`, `bot/handlers.py`, `bot/keyboards.py`, `bot/states.py`, `bot/participants.py`, maybe-ping callback path, `access_groups.py` ACL helper
- Admin callbacks e.g. `admin:approve:{event_id}:{user_id}` / `admin:reject:{event_id}:{user_id}` — must be admin-gated
- Defaults locked in ADR-025 / S-213
- Suggested tests: new `test_registration_approval.py`; extend participants, admin notify, maybe pings, broadcast/reminder, access groups

## Verification (agents)

1. [ ] `PYTHONPATH=. pytest -q` in `apps/zarya-tg/backend`
2. [ ] Lint for touched Python as required by CI
3. [ ] CI green on the implementation PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
