# T-210 — Frontend: home poster slider


## Human summary (review this first)

**Will do:**
- Add a ~half-screen poster slider on the home screen for events with `is_featured` from the existing events list
- Show date-time and name on each poster; tap opens the same event details as a list card
- Keep the current event list below; hide the slider when there are no featured events

**Will not do:**
- Backend/bot changes (T-209)
- Search, filters, autoplay, or a carousel library
- Changing `EventCard` layout or adding a slider on «Мои регистрации»
- Client-side access-group filtering (trust `GET /api/events`)

**Touched areas:** Mini App home (`App.tsx`), new `PosterSlider` component, `Event` type in API client

**Risk:** Low–Medium — layout height on small Telegram WebViews; treat missing `is_featured` as false for older API

**Smoke check after merge:**
- With T-209 deployed: featured public event → slider + list; tap poster → details
- Non-featured only → list as today, no slider
- One featured → single poster without dots; several → swipeable snap carousel
- Frontend lint/build pass

**Reviewer decision:** `[x] Approved to implement` · `[ ] Needs changes` · Reviewer: product (chat) · Date: 2026-08-05

---

| Field | Value |
|-------|-------|
| ID | T-210 |
| Title | Frontend home poster slider |
| Status | `done` |
| Spec / ADR | [S-209](../specs/S-209-home-poster-slider.md), [ADR-021](../decisions/021-home-featured-slider.md), [ADR-002](../decisions/002-ux-navigation.md) |
| App | `zarya-tg` |
| Estimate | S |

## Goal

Render ACL-visible featured events as a large poster slider above the existing home event list.

## Acceptance Criteria

- [x] `Event` type / `normalizeEvent` include `is_featured` (missing → false)
- [x] New `PosterSlider` (~50vh): cover via `CoverImage`, bottom gradient, overlay `formatEventDate` + `name`
- [x] Home (`screen === "home"`): if any `events.filter(e => e.is_featured)`, render slider above `.event-list`; else list only
- [x] Slide tap calls the same handler as list cards (`setSelectedEventId` / open details)
- [x] 1 featured → no dots/swipe chrome required; N → CSS `scroll-snap` horizontal carousel; no autoplay; no new npm carousel dependency
- [x] `EventCard` and registrations screen unchanged (no slider)
- [x] Russian accessible labels on interactive slides
- [x] `npm run lint` and `npm run build` pass

## Out of Scope

- Setting `is_featured` (T-209)
- Platinumlist search/chips/video
- Location or ✅ on posters
- Changing empty-state copy

## Implementation Notes

- Key files: `frontend/src/App.tsx`, `App.css`, new `components/PosterSlider.tsx` + `.css`, `api/client.ts`, reuse `CoverImage`, `formatEventDate`
- Depends on T-209 for real data; can develop against mocked `is_featured` or after T-209 merges
- Preserve list order from API (already chronological); featured subset keeps that relative order
- Respect dark/light tokens from `index.css` / theme

## Verification

1. [x] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
2. [x] Manual or component smoke: 0 / 1 / N featured layouts (implemented; needs device smoke on deploy)
3. [x] CI green on the PR
4. [x] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/13
- Defaults chosen: ~50vh; dots only when >1; no autoplay; peek of adjacent slides (~88% width)
- Residual risks: very long titles use 2-line clamp on overlay
