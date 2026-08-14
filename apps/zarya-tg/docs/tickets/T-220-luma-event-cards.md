# T-220 — Mini App: Luma-style event cards on home and «Мои»


## Human summary (review this first)

**Will do:**
- Restyle list cards: ~80px rounded thumb, «Иду» / «Подумаю» overlay on the photo, title, clock + pin meta (no corner ✅ and no 📍 paragraph)
- Group the home (and upcoming «Мои») list with date headers when there are two or more different days
- Keep the featured slider at ~50vh and keep featured events in the list

**Will not do:**
- Event details RSVP circles, Telegram BackButton, header word labels (T-221 / T-222)
- Guest lists, filters, bigger posters, hiding featured from the list
- Backend, bot, or API changes

**Touched areas:** Mini App `EventCard`, home / registrations lists in `App.tsx`, card CSS

**Risk:** Low — presentation only; RSVP behavior unchanged

**Smoke check after merge:**
- Featured slider still shows with the list visible underneath; featured event also in the list
- Going card shows «Иду» on the thumb; maybe shows «Подумаю»; archive thumbs have no overlay
- Two days of events → date headers; one day → no extra header required
- Frontend lint/build pass

**Reviewer decision:** `[x] Approved to implement` · `[ ] Needs changes` · Reviewer: product · Date: 2026-08-14  
**DoR:** `[x] Approved` — Human summary approved with S-024 / ADR-024 (implement request 2026-08-14)

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-220 |
| Title | Luma-style event cards + date headers |
| Status | `in_review` |
| Spec / ADR | [S-024](../specs/S-024-mini-app-visual-refresh.md), [ADR-024](../decisions/024-mini-app-visual-language.md), [ADR-021](../decisions/021-home-featured-slider.md), [ADR-023](../decisions/023-past-events-archive.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Make the chronological event list scannable like Luma’s compact rows without changing slider height or RSVP rules.

## Acceptance Criteria

- [x] `EventCard` thumb stays ~80px rounded square (not 16:9 full-width); status overlay bottom-left **Иду** / **Подумаю**; no corner ✅ / … emoji
- [x] Meta is two lines with outline clock + pin icons; location has no `📍` text prefix; title remains primary
- [x] Archive / `completed` cards stay muted and **do not** show Иду/Подумаю overlays (ADR-023)
- [x] Home and upcoming «Мои» lists group by calendar day when **2+ distinct dates**; headers like `Сегодня / пт` using existing Russian date helpers; single-day lists need no header
- [x] `PosterSlider` height, featured-in-list, and tap-to-details unchanged (ADR-021)
- [x] `npm run lint` and `npm run build` pass in `apps/zarya-tg/frontend`

## Out of Scope

- Circular RSVP, BackButton, header copy, empty-state rewrite, English details strings (T-221 / T-222)
- De-duplicating featured events from the list
- Changing `is_featured` / API / bot
- Bottom tabs, guest list, filters

## Implementation Notes

- Key files: `frontend/src/components/EventCard.tsx` + `.css`, `frontend/src/App.tsx`, `frontend/src/utils/format.ts` (reuse `formatEventDate`; add a small day-key helper if needed)
- Prefer a tiny shared SVG module (`components/icons.tsx`) for clock/pin; T-221 will add check/pause/share/calendar
- Overlay colors: going green / maybe amber tokens — introduce in `index.css` if missing (T-222 may complete the type scale)
- Grouping: derive `date` from each `Event`; stable order = API order within a day
- Tests: none required beyond lint/build unless a pure date-header helper is extracted (then unit-test the helper)

## Verification

1. [x] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
2. [ ] Manual smoke: 0/1/N featured; going/maybe/plain/archive cards; 1-day vs 2-day lists
3. [ ] CI green on the PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/23
- Defaults chosen (if any): Date headers only on upcoming home / «Мои» lists (not Архив). Group key is `event.date`, not the formatted header string.
- Residual risks: Visual smoke still needed on a real Telegram client.
