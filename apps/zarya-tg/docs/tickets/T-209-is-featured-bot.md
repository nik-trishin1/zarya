# T-209 — Backend: `is_featured` + admin bot create/edit


## Human summary (review this first)

**Will do:**
- Add `events.is_featured` (default false) and expose it on event API responses
- Let admin set featured in Telegram bot create and edit flows (Да / Нет; edit also Оставить)
- Keep list/detail ACL unchanged — featured does not bypass access groups

**Will not do:**
- Mini App slider UI (T-210)
- Separate featured endpoint or admin menu
- Editing audience or capacity on edit
- Auto-featuring events

**Touched areas:** event DB column, event schemas/services, admin bot create/edit FSM, API event JSON

**Risk:** Low — additive boolean; ACL path unchanged. Main risk is forgetting featured on edit confirm or defaulting to true.

**Smoke check after merge:**
- Create event with «Слайдер: да» → `GET /api/events` includes `is_featured: true` for an entitled user
- Create Core featured event → non-member list omits it; member/admin see `is_featured: true`
- Edit to turn featured off → response shows false
- pytest for schema persist + visibility matrix

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

| Field | Value |
|-------|-------|
| ID | T-209 |
| Title | Backend is_featured + bot create/edit |
| Status | `todo` |
| Spec / ADR | [S-209](../specs/S-209-home-poster-slider.md), [ADR-021](../decisions/021-home-featured-slider.md), [ADR-020](../decisions/020-access-groups.md) |
| App | `zarya-tg` |
| Estimate | S |

## Goal

Persist and expose an admin-controlled `is_featured` flag so the Mini App can build a home poster slider without a new API or ACL path.

## Acceptance Criteria

- [ ] `events.is_featured` exists (`BOOLEAN NOT NULL DEFAULT FALSE`) via model + `schema_updates`
- [ ] `create_event` / `update_event` accept `is_featured`; API `EventResponse` includes it (default false for old clients)
- [ ] Create FSM: after audience, prompt «Показать в слайдере на главной?» with Да / Нет; value stored and shown on confirm
- [ ] Edit FSM: can change featured (Да / Нет / Оставить) with current value shown; confirm reflects it; `update_event` persists
- [ ] `GET /api/events` still filters by upcoming + access groups; featured group events stay hidden from non-members
- [ ] Backend tests: default false; create/edit persist; featured Core event visible to member/admin only
- [ ] No Mini App UI changes in this ticket

## Out of Scope

- `PosterSlider` / home layout (T-210)
- Featured-only endpoint
- Changing audience or `max_participants` on edit
- PRD mockup image refresh (optional follow-up)

## Implementation Notes

- Key files: `backend/app/models/event.py`, `schema_updates.py`, `schemas/event.py`, `services/events.py`, `utils/formatting.py` (if response mapping is centralized), `bot/states.py`, `bot/keyboards.py`, `bot/handlers.py`
- Mirror audience Yes/No callback pattern for featured
- `update_event` skips `None` but must accept `False` for clearing featured — pass boolean explicitly
- Suggested tests: extend `test_events.py` / `test_api_events.py` / `test_access_groups.py`

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in `apps/zarya-tg/backend`
2. [ ] Lint/typecheck for touched Python as required by CI
3. [ ] CI green on the PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL:
- Defaults chosen: create defaults to not featured (Нет); chronological ordering unchanged; no separate featured query
- Residual risks:
