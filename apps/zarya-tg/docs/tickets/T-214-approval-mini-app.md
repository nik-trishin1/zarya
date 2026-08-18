# T-214 — Mini App: registration approval UI


## Human summary (review this first)

**Will do:**
- On «по заявке» events, change the going CTA to «Записаться»; after tap show «На рассмотрении» and «Отменить заявку»
- Put pending events in «Мои регистрации» with a distinct badge (not «Иду»)
- Hide calendar and +1 until the application is accepted; keep «Подумаю» until the user applies
- Trust T-213 fields: `requires_approval`, `is_pending`

**Will not do:**
- Backend/bot (T-213)
- Price / fact-row restyle (T-215)
- Waitlist copy, decline reasons, or showing other applicants

**Touched areas:** Mini App event details RSVP, list/card badges, «Мои» list, API client types

**Risk:** Low–medium — mixing pending with `is_registered` would unlock calendar too early or drop applications from «Мои»

**Smoke check after merge:** Approval event → «Записаться» → overlay «На рассмотрении», guest count unchanged, event under «Мои», no calendar → after accept (API) UI looks like a normal going RSVP

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____  
**DoR:** `[ ] Not ready` — Human summary + S-213 must be approved; implement after T-213 API exists

---

| Field | Value |
|-------|-------|
| ID | T-214 |
| Title | Mini App registration approval UI |
| Status | `todo` |
| Spec / ADR | [S-213](../specs/S-213-manual-registration-approval.md), [ADR-025](../decisions/025-manual-registration-approval.md), [ADR-024](../decisions/024-mini-app-visual-language.md) |
| App | `zarya-tg` |
| Estimate | S |

## Goal

Make pending applications visible and controllable in the Mini App without treating them as confirmed attendance.

## Acceptance criteria

- [ ] Client types/`normalizeEvent`: `requires_approval`, `is_pending` (missing → false); `is_registered` still going-only
- [ ] Approval event, not going/pending: going circle caption **«Записаться»**; +1 chip still applies at apply time; toast uses API message (expect «Заявка отправлена. Ждём подтверждения.»)
- [ ] `is_pending`: overlay **«На рассмотрении»**; selected going circle **or** equivalent pending visual (not maybe amber, not «Иду»); **«Отменить заявку»**; no calendar; no share-as-going unless already specified for registered only; no «Подумаю»; no +1 chip until active
- [ ] After accept (`is_registered`): existing «Буду» / «Иду» / calendar / +1 / «Отменить регистрацию»
- [ ] «Подумаю» hidden while pending or going; still available when neither
- [ ] Full + not pending: «Мест нет», cannot apply (same as cannot «Буду»)
- [ ] «Мои регистрации» shows pending upcoming (T-213 `/my`); header ticket count includes them
- [ ] Archive/read-only: no new apply
- [ ] `npm run lint` and `npm run build` pass

## Out of scope

- T-213 / T-215
- Admin Mini App
- Pending on poster slider overlay (list card is enough)

## Implementation notes (for agents)

- Key files: `frontend/src/api/client.ts`, `components/EventDetails.tsx` + css, `components/EventCard.tsx` + css, `App.tsx` / `Header.tsx` if badge counts assume `is_registered` only
- Keep RSVP circles (ADR-024); do not add a third circle for pending
- Treat missing `is_pending` as false for older backends
- Depends on T-213 for real data

## Verification (agents)

1. [ ] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
2. [ ] CI green on the PR
3. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
