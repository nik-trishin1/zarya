# T-211 — Maybe RSVP («Подумаю») + delayed bot ping


## Human summary (review this first)

**Will do:**
- Add a third RSVP state «Подумаю» (`maybe`) that does not take a seat
- On mark, precompute **all remaining** ping milestones (7d / 3d / 2d / 24h before start) and keep sending them while status stays `maybe` — even if the user ignores earlier pings
- Bot DMs use **«Буду»** / **«Не смогу»**
- Show maybe distinctly in the Mini App (not as registered ✅)
- Show maybe people in admin «Участники» as `N. Имя @username - Подумаю` (after confirmed guests; `Всего` = active seats only)
- Include maybe users in participant broadcasts («Написать участникам») with the same message as going guests

**Will not do:**
- Soft-hold capacity or waitlists
- Put maybe users into calendar export or «Мои регистрации»
- Change the existing 24h reminder for confirmed (`active`) guests (ADR-013)
- party_size / +1 while still maybe
- Admin DM notify on mark «Подумаю» (ADR-005 stays going/cancel only)

**Touched areas:** registrations model/API, Mini App event details + list badges, bot scheduler + inline callbacks, admin participant list, participant broadcast recipient query

**Risk:** Medium — must split broadcast vs reminder recipient queries so widening broadcast to maybe cannot leak into ADR-013; capacity/.ics/my-regs stay active-only

**Smoke check after merge:** Mark «Подумаю» on a far-out event → 4 schedule rows; capacity unchanged; admin list shows `… - Подумаю`; «Написать участникам» preview count includes maybe; ignore first ping → later still fires; «Буду» when full stays maybe; calendar hidden for maybe

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-08-12  
**DoR:** `[x] Approved` (Human summary + ADR-022 locked, including broadcast inclusion)

---

| Field | Value |
|-------|-------|
| ID | T-211 |
| Title | Maybe RSVP («Подумаю») + delayed bot ping |
| Status | `todo` (factory-ready) |
| Spec / ADR | [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md); broadcast [ADR-007](../decisions/007-participant-broadcast.md); capacity [ADR-012](../decisions/012-event-capacity-limit.md); 24h reminder [ADR-013](../decisions/013-event-reminder-24h.md); party size [ADR-019](../decisions/019-registration-party-size.md); admin list [ADR-006](../decisions/006-admin-participant-list.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Let users park interest with «Подумаю» without taking a seat; nudge them at each upcoming milestone until they confirm or decline; let admins see and message interest.

## Acceptance Criteria

- [ ] `registrations.status` supports `maybe`; ping schedule table (per-offset `due_at` / sent tracking) exists via models + schema_updates as needed
- [ ] Marking maybe inserts schedule entries for every future offset in `{7d, 3d, 2d, 24h}`; past offsets skipped; past events reject maybe; maybe does not change `SUM(party_size)` / `is_full`
- [ ] While status remains `maybe`, each due unsent entry is delivered once (ignore does not cancel later entries); leaving `maybe` clears unsent entries; re-mark rebuilds remaining future offsets
- [ ] API exposes current-user RSVP including maybe; `is_registered` remains **active-only**; Mini App shows **«Подумаю»** and a non-✅ maybe indicator; no calendar/+1 while maybe; no «Подумаю» while already going
- [ ] Scheduler uses the same hourly MSK 08–22 loop pattern as ADR-013 (~±1h window around `due_at`)
- [ ] Ping inline **«Буду»** → `active` with `party_size=1`; if full → stay maybe + keep schedule + user message; **«Не смогу»** → `cancelled`
- [ ] ADR-013 active reminders unchanged; reminder recipient query stays active-only (must not share a blindly widened helper with broadcasts)
- [ ] Admin «Участники»: active lines seat-expanded as today; then maybe lines `N. Имя @username - Подумаю`; `Всего` = active seats only
- [ ] Participant broadcast recipients = `active` ∪ `maybe` (ADR-007); empty-state copy works when only maybe exist
- [ ] «Мои регистрации» and .ics remain active-only
- [ ] Group-event ACL treats maybe like active for registration escape hatch
- [ ] Backend tests cover schedule build, cascade after ignore, capacity isolation, admin list, broadcast≠reminder recipients, callbacks, calendar 403 for maybe; frontend lint/build pass

## Out of Scope

- Waitlist or seat hold for maybe
- party_size / +1 while still maybe
- Maybe in calendar export or «Мои регистрации»
- Admin notify on mark maybe (ADR-005)
- Dedicated maybe-only broadcast tool
- Separate interest table

## Implementation Notes

- Key files: `models/registration.py`, new schedule model, `schema_updates.py`, `services/events.py` (`get_event_registered_users` — **split or add status filter**), `services/participant_broadcast.py` / handlers, `bot/participants.py`, maybe-ping module next to `event_reminders.py`, `run.py`, `bot/handlers.py` + keyboards, `frontend` EventDetails / EventCard / client types, `access_groups.py` ACL helper
- Prefer child table `registration_maybe_pings` (registration_id, offset_id, due_at, sent_at)
- Defaults locked in ADR-022 §8–9 (broadcast same body; admin label; full-on-Буду stays maybe; no ADR-005 on maybe)

## QA / integrity review (pre-implement, 2026-08-12)

### Must not break

| Area | Guard |
|------|--------|
| Capacity / `is_full` / guest counters | Keep `SUM(party_size)` on `active` only |
| ADR-013 24h going reminder | Recipients stay `active` only — **split query from broadcast** |
| «Мои регистрации» / .ics | Gate on `is_registered` (active); do not set true for maybe |
| ADR-017 all-users / group broadcasts | Unrelated; leave alone |
| `UniqueConstraint(user_id, event_id)` | One row; status transitions only |

### Highest regression risk

Widening `get_event_registered_users()` for broadcasts without a status parameter would accidentally DM maybe users the “Ждем вас уже завтра!” going reminder. **Required fix:** explicit status filter or separate `get_event_broadcast_recipients()`.

### Frontend traps

- Keep `is_registered` = going only; add `rsvp_status` or `is_maybe`
- Hide calendar and +1 while maybe
- Allow «Подумаю» when event is full (does not take a seat)
- Do not offer «Подумаю» while `is_registered`

### Suggested tests

`test_maybe_pings.py` (schedule + cascade); extend `test_participant_broadcast.py`, `test_event_reminders.py` (maybe excluded), `test_participants.py` (label + Всего), `test_events.py` (capacity + RSVP API), `test_access_groups.py` (maybe ACL), bot callback tests for Буду full / Не смогу.

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green on the implementation PR
4. [ ] Separate review pass requested (`process/ai-factory/REVIEW_PASS.md`)

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
