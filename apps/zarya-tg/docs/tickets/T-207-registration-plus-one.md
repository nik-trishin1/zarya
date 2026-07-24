# T-207 — Register alone or with +1 (party_size)


## Human summary (review this first)

**Will do:**
- Let users register alone or with +1 (two seats)
- Allow add/remove +1 after registration when seats allow
- Count capacity as sum of seats; expand admin guest list to match seat count

**Will not do:**
- Identify or name the +1 guest
- Partial cancel of only the +1 without an explicit "remove +1" action
- Waitlists or party_size > 2 in the UI

**Touched areas:** registrations API/model, event capacity counts, Mini App event details, admin participant list

**Risk:** Medium — capacity edge cases when one seat remains; all counters must switch from COUNT to SUM

**Smoke check after merge:** Register with +1 on a limited event → guest count +2; with 1 seat left, +1 muted; admin list shows duplicate "Name + 1" line

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-07-24

---

| Field | Value |
|-------|-------|
| ID | T-207 |
| Title | Registration party size (+1) |
| Status | `done` |
| Spec / ADR | [ADR-019](../decisions/019-registration-party-size.md), capacity [ADR-012](../decisions/012-event-capacity-limit.md), admin list [ADR-006](../decisions/006-admin-participant-list.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Users can take one or two seats under a single registration; +1 can be added or removed later without identifying the guest.

## Acceptance Criteria

- [x] `registrations.party_size` exists (default 1); active seat count is `SUM(party_size)`
- [x] POST register accepts `party_size` 1 or 2; rejects when not enough seats (409)
- [x] PATCH updates `party_size` for an existing registration; +1 blocked when only one seat free
- [x] DELETE cancel removes the whole registration (both seats)
- [x] Mini App: choose Один / +1 at register; after register, add or remove +1 (muted when unavailable)
- [x] Event responses include current user `party_size`
- [x] Admin «Участники» expands +1 into a second numbered line (`Имя + 1`); total equals seats
- [x] Reminders/broadcasts still one message per user
- [x] Backend tests cover capacity + party_size; frontend lint/build pass

## Out of Scope

- Naming or inviting the +1 person
- party_size > 2 in product UI (schema remains extensible)
- Editing capacity in admin edit flow (unchanged from ADR-012)

## Implementation Notes

- Key files: `models/registration.py`, `schema_updates.py`, `services/events.py`, `api/registrations.py`, `bot/participants.py`, `frontend` EventDetails + client
- Prefer PATCH for post-register party_size changes over a second POST
- Suggested tests: register +1 takes two seats; upgrade blocked at capacity-1; admin list expansion; cancel frees both seats

## Verification

1. [x] `PYTHONPATH=. pytest -q` in backend (67 passed)
2. [x] `npm run lint && npm run build` in frontend
3. [ ] CI green
4. [ ] Review pass against AC

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/10
- Defaults: MVP max party_size = 2; +1 line label `Имя + 1` without @username on the guest line
- Residual risks: concurrent register race near capacity (same as ADR-012)
