# T-211 — Maybe RSVP («Подумаю») + delayed bot ping


## Human summary (review this first)

**Will do:**
- Add a third RSVP state «Подумаю» (`maybe`) that does not take a seat
- On mark, precompute **all remaining** ping milestones (7d / 3d / 2d / 24h before start) and keep sending them while status stays `maybe` — even if the user ignores earlier pings
- Bot DMs use **«Буду»** / **«Не смогу»**
- Show maybe distinctly in the Mini App (not as registered ✅)
- Show maybe people in admin «Участники» as `Имя - Подумаю` (after confirmed guests; not counted as seats)

**Will not do:**
- Soft-hold capacity or waitlists
- Put maybe users into calendar export or participant broadcasts
- Change the existing 24h reminder for confirmed (`active`) guests (ADR-013)
- party_size / +1 while still maybe

**Touched areas:** registrations model/API, Mini App event details + list badges, bot scheduler + inline callbacks, admin participant list formatting

**Risk:** Medium — capacity and broadcasts must stay active-only while admin list and cascade pings correctly include maybe

**Smoke check after merge:** Mark «Подумаю» on a far-out event → schedule has 7d+3d+2d+24h; capacity unchanged; admin list shows `Имя - Подумаю`; ignoring first ping still delivers the next due one; «Буду» / «Не смогу» clear remaining schedule

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-08-12

---

| Field | Value |
|-------|-------|
| ID | T-211 |
| Title | Maybe RSVP («Подумаю») + delayed bot ping |
| Status | `todo` |
| Spec / ADR | [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md); capacity [ADR-012](../decisions/012-event-capacity-limit.md); 24h reminder [ADR-013](../decisions/013-event-reminder-24h.md); party size [ADR-019](../decisions/019-registration-party-size.md); admin list [ADR-006](../decisions/006-admin-participant-list.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Let users park interest with «Подумаю» without taking a seat; nudge them at each upcoming milestone before the event until they confirm or decline; let admins see interest in «Участники».

## Acceptance Criteria

- [ ] `registrations.status` supports `maybe`; a ping schedule (per-offset `due_at` / sent tracking) exists via schema_updates
- [ ] Marking maybe inserts schedule entries for every future offset in `{7d, 3d, 2d, 24h}`; past offsets skipped; maybe does not change `SUM(party_size)` / `is_full`
- [ ] While status remains `maybe`, each due unsent entry is delivered once (ignore does not cancel later entries); leaving `maybe` clears unsent entries; re-mark rebuilds remaining future offsets
- [ ] API exposes current-user RSVP including maybe (not only boolean `is_registered`); Mini App shows **«Подумаю»** and a non-✅ maybe indicator
- [ ] Scheduler uses the same hourly MSK 08–22 loop pattern as ADR-013 (~±1h window around `due_at`)
- [ ] Ping inline **«Буду»** → `active` with `party_size=1` (409/message if full); **«Не смогу»** → `cancelled` / clear maybe
- [ ] ADR-013 active reminders unchanged; maybe users are excluded from them
- [ ] Admin «Участники»: active lines seat-expanded as today; then maybe lines as `Имя - Подумаю`; capacity totals remain active-only
- [ ] «Мои регистрации», .ics, participant broadcast remain active-only
- [ ] Backend tests cover schedule build (far vs near event), cascade after ignore, capacity isolation, admin list label, and callback transitions; frontend lint/build pass

## Out of Scope

- Waitlist or seat hold for maybe
- party_size / +1 while still maybe
- Maybe in calendar export or participant broadcasts
- Separate interest table
- Dedicated admin “maybe-only” broadcast tool

## Implementation Notes

- Key files (expected): `models/registration.py`, `schema_updates.py`, `services/events.py`, `api/registrations.py`, schemas, maybe-ping module next to `event_reminders.py`, `run.py`, `bot/handlers.py` + keyboards, `bot/participants.py` (or admin list formatter), `frontend` EventDetails / EventCard / client types
- Prefer a small schedule table (or JSON entries) keyed by registration + offset id; pure function to build remaining offsets from `event_start` and `now`
- Reuse `deliver_bot_message` and daytime gate from the existing reminder loop
- Defaults: bot «Буду» always `party_size=1`; user can add +1 later in the Mini App if allowed; admin maybe label exactly ` - Подумаю` suffix (Russian)

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green on the implementation PR
4. [ ] Separate review pass requested (`process/ai-factory/REVIEW_PASS.md`)

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
