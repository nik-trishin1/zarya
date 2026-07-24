# T-203 — Past events status and archive


## Human summary (review this first)

**Will do:**
- Keep the main feed upcoming-only
- Show past registrations in an Archive section labeled «Завершено»

**Will not do:**
- Delete past events from the database
- Bring past events back into the main home feed

**Touched areas:** Event lists, «Мои регистрации», possibly admin list

**Risk:** Medium — date-boundary edge cases around midnight

**Smoke check after merge:** Register for a past-dated test event → appears under Архив, not home

**Reviewer decision:** `[ ] Approved to implement`

---

| Field | Value |
|-------|-------|
| ID | T-203 |
| Title | Show past events as completed with archive section |
| Status | `todo` |
| Spec / ADR | Builds on [ADR-018](../decisions/018-hide-past-events.md); needs short UI spec in this ticket |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Past events are no longer only hidden: users can see a clear «Завершено» state and browse an Archive section.

## Acceptance Criteria

- [ ] Home list remains upcoming-only (ADR-018 unchanged for the main feed)
- [ ] «Мои регистрации» shows past registered events in an «Архив» section with visual «Завершено» treatment (Russian UI)
- [ ] Admin manage list can still find past events (existing admin path or explicit archive), without deleting DB rows
- [ ] Optional 48h grace: events remain on home until local calendar date + 0 days unless a follow-up ADR says otherwise — **default: no grace** (match ADR-018 midnight boundary)
- [ ] Backend tests cover past vs upcoming filtering for the archive endpoint or query used by the UI
- [ ] Frontend lint + build pass

## Out of Scope

- Photo galleries / post-event content
- Restoring past events to the main chronological feed

## Implementation Notes

- Likely touch: `backend/app/services/events.py`, registrations list API, frontend home/registrations screens
- Prefer extending existing list endpoints with a `include_past` / separate archive fetch over duplicating models

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green
4. [ ] Review pass against AC
