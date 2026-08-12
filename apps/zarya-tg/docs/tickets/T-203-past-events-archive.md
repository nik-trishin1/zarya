# T-203 — Past events status and archive


## Human summary (review this first)

**Will do:**
- Keep the main feed upcoming-only (ADR-018)
- In «Мои регистрации»: upcoming `active` registrations on top, then section **«Архив»** for past events where user was **«Буду»** (`active` only — not «Подумаю»)
- Archive cards: muted UI + **«Завершено»**; opening = read-only details, **no calendar**
- Admin bot: **«Архив»** listing past events — view detail + **«Участники»** only (no edit/delete)
- New API `GET /api/registrations/my/archive`; past admin query for bot archive list
- Midnight date boundary, no time limit on how far back archive goes

**Will not do:**
- Delete past events from the database
- Show past events on the home feed
- Include `maybe` in user archive
- Edit/delete past events in admin archive (T-302 duplicate later)
- Calendar export from archive
- 48h grace before hiding from upcoming lists

**Touched areas:** `events.py` list queries, registrations API, `App.tsx` / `EventCard` / `EventDetails`, admin bot manage + archive handlers

**Risk:** Medium — date boundary at midnight; keep upcoming vs archive queries clearly separate

**Smoke check after merge:** User with `active` reg on an event whose date is yesterday → event in «Архив», not in upcoming list or home; `maybe`-only past reg absent from archive; admin opens past event from «Архив» and sees participants

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-08-12  
**DoR:** `[x] Approved`

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/18
- Defaults chosen: readOnly from archive context (not is_past); separate admin archive callbacks
- Residual risks: date boundary uses server `date.today()` (ADR-018 pattern)

---

| Field | Value |
|-------|-------|
| ID | T-203 |
| Title | Past events archive («Архив» / «Завершено») |
| Status | `done` |
| Spec / ADR | [ADR-023](../decisions/023-past-events-archive.md), extends [ADR-018](../decisions/018-hide-past-events.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Users and admins can browse completed events without cluttering active lists.

## UI spec (Mini App)

**«Мои регистрации» screen**

```
[ upcoming EventCard × N ]     ← active, date >= today, same as today

── Архив ──                     ← section header, only if archive non-empty

[ EventCard muted + «Завершено» × M ]
```

- Empty upcoming + empty archive → «Вы не зарегистрированы ни на какие события»
- Empty upcoming + has archive → show only «Архив» section (no misleading empty upcoming message)
- 🎫 counter = upcoming `active` count only

**Archive event details:** name, date, location, description, cover; banner «Событие завершено» / «Завершено»; no action buttons (no register, maybe, calendar, share optional — omit share to keep simple)

## UI spec (admin bot)

- `/admin` menu: add **«Архив»** (or under manage — product default: sibling to «Управлять событиями»)
- List past events newest-first; tap → same detail layout as manage but **without** edit/delete/broadcast actions; keep **«Участники»**
- Event rows remain keyed by `event_id` for future [T-302](T-302-event-duplication.md) «Дублировать» on this screen

## Acceptance Criteria

- [ ] Home + `GET /api/events` + `GET /api/registrations/my` remain upcoming-only, `active` only
- [ ] `GET /api/registrations/my/archive` returns past events (`date < today`) with `active` registration only; excludes `maybe`
- [ ] «Мои регистрации» renders upcoming block + «Архив» block per UI spec; archive cards show «Завершено»
- [ ] Archive event details read-only; no calendar links/buttons
- [ ] 🎫 counter unchanged (upcoming `active` only)
- [ ] Admin «Архив» lists past events; detail + participants work; no edit/delete/broadcast on archived events
- [ ] Backend tests: archive vs upcoming filters, maybe excluded, admin past list
- [ ] Frontend lint + build pass

## Out of Scope

- `maybe` in archive
- Photo galleries / post-event content
- Past events on home feed
- Admin edit/delete in archive
- Calendar from archive
- T-302 duplicate button (follow-up; architecture allows `event_id` from archive detail)

## Implementation Notes

- Backend: `get_past_registered_events(db, user)` mirroring `get_upcoming_events(..., registered_only=True)` with `date < today` and `status == active`; `get_past_events_admin(db)` for bot
- Frontend: `fetchMyArchive()` in client; `App.tsx` merges two lists on registrations screen; `EventCard` variant `completed` prop
- `EventDetails`: `readOnly` or infer from `is_past` + archive context
- Do not widen `get_upcoming_events` with a flag that risks regressing home/admin upcoming filters

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green
4. [ ] Review pass (`process/ai-factory/REVIEW_PASS.md`)

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
