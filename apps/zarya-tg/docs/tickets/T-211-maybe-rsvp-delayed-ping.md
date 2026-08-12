# T-211 — Maybe RSVP («Подумаю») + delayed bot ping


## Human summary (review this first)

**Will do:**
- Add a third RSVP state «Подумаю» (`maybe`) that does not take a seat
- On mark, precompute one `maybe_ping_at` from the ADR-022 tier table (7d / 3d / 2d / 24h before the event)
- Bot DMs the user near that time with **«Буду»** / **«Не смогу»**
- Show maybe distinctly in the Mini App (not as registered ✅)

**Will not do:**
- Soft-hold capacity or waitlists
- Repeat pings if the user ignores the first
- Put maybe users on admin guest lists, calendar export, or participant broadcasts
- Change the existing 24h reminder for confirmed (`active`) guests (ADR-013)

**Touched areas:** registrations model/API, Mini App event details + list badges, bot scheduler + inline callbacks

**Risk:** Medium — every `active`-only filter must stay correct so maybe never inflates capacity or guest lists

**Smoke check after merge:** Mark «Подумаю» on a far-out event → `maybe_ping_at` ≈ start−7d; capacity unchanged; after simulated due tick, bot message has Буду/Не смогу and resolves status

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

| Field | Value |
|-------|-------|
| ID | T-211 |
| Title | Maybe RSVP («Подумаю») + delayed bot ping |
| Status | `todo` |
| Spec / ADR | [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md); capacity [ADR-012](../decisions/012-event-capacity-limit.md); 24h reminder [ADR-013](../decisions/013-event-reminder-24h.md); party size [ADR-019](../decisions/019-registration-party-size.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Let users park interest with «Подумаю» without taking a seat, and have the bot ask once before the event whether they will come.

## Acceptance Criteria

- [ ] `registrations.status` supports `maybe`; columns `maybe_ping_at` and `maybe_ping_sent_at` exist (schema_updates)
- [ ] Marking maybe sets `maybe_ping_at` per ADR-022 tiers and clears `maybe_ping_sent_at`; maybe does not change `SUM(party_size)` / `is_full`
- [ ] API exposes current-user RSVP including maybe (not only boolean `is_registered`); Mini App shows **«Подумаю»** and a non-✅ maybe indicator
- [ ] Scheduler (same hourly MSK 08–22 loop pattern as ADR-013) sends at most one maybe ping per cycle; stamps `maybe_ping_sent_at`
- [ ] Ping inline **«Буду»** → `active` with `party_size=1` (409/message if full); **«Не смогу»** → `cancelled` / clear maybe
- [ ] ADR-013 active reminders unchanged; maybe users are excluded from them
- [ ] «Мои регистрации», .ics, admin guest list, participant broadcast remain active-only
- [ ] Backend tests cover tier `maybe_ping_at` calculation, capacity isolation, and callback status transitions; frontend lint/build pass

## Out of Scope

- Waitlist or seat hold for maybe
- Second/third nags after no reply
- party_size / +1 while still maybe
- Admin UI to list or message maybe-only users
- Separate interest table

## Implementation Notes

- Key files (expected): `models/registration.py`, `schema_updates.py`, `services/events.py`, `api/registrations.py`, `schemas/event.py` / registration schemas, `services/event_reminders.py` or sibling maybe-ping module, `run.py`, `bot/handlers.py` + keyboards, `frontend` EventDetails / EventCard / client types
- Prefer computing `maybe_ping_at` in one pure function tested by unit tests (tier table from ADR-022)
- Reuse `deliver_bot_message` and daytime gate from the existing reminder loop
- Defaults: bot «Буду» always `party_size=1`; user can add +1 later in the Mini App if allowed

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green on the implementation PR
4. [ ] Separate review pass requested (`process/ai-factory/REVIEW_PASS.md`)

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
