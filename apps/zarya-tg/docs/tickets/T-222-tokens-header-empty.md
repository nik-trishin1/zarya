# T-222 — Mini App: tokens, header chrome, empty states


## Human summary (review this first)

**Will do:**
- Tighten the design tokens (type scale; RSVP green/amber only on badges/circles) while keeping zarya orange and paper/dark backgrounds
- Label the existing ticket toggle with words: «Мои» + count on home, «События» on registrations (no bottom tabs)
- Warmer two-line empty states on home and «Мои»

**Will not do:**
- Card layout or RSVP circles (T-220 / T-221)
- Bottom tab bar, guest list, API/bot, or replacing brand colors with raw Telegram `themeParams`

**Touched areas:** `index.css`, `Header`, home/registrations empty copy in `App.tsx`, shared icons if still duplicated

**Risk:** Low — chrome and tokens only

**Smoke check after merge:**
- Home header: «События» + «Мои» with upcoming-registration count; toggle still switches screens
- Empty home and empty «Мои» show icon + two Russian lines
- Light and dark themes still use paper/dark + `#e8874a`
- Frontend lint/build pass

**Reviewer decision:** `[x] Approved to implement` · `[ ] Needs changes` · Reviewer: product · Date: 2026-08-14  
**DoR:** `[x] Approved` — Human summary approved with S-024 / ADR-024 (implement request 2026-08-14)

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-222 |
| Title | Tokens, header chrome, empty states |
| Status | `in_review` |
| Spec / ADR | [S-024](../specs/S-024-mini-app-visual-refresh.md), [ADR-024](../decisions/024-mini-app-visual-language.md), [ADR-002](../decisions/002-ux-navigation.md), [ADR-003](../decisions/003-language.md) |
| App | `zarya-tg` |
| Estimate | S |

## Goal

Make chrome feel native to Telegram and to the new list/RSVP language without adding a third screen or tab bar.

## Acceptance Criteria

- [x] `index.css` keeps `--color-accent: #e8874a` and existing paper/dark surfaces; adds title/meta/body type scale; RSVP green/amber used only for going/maybe chrome
- [x] Header toggle is still a single control (ADR-002): home **Мои** + upcoming `active` count; registrations **События**; titles **События** / **Мои регистрации**; `aria-label` includes count on home
- [x] Empty home: **Нет предстоящих событий** + **Загляните позже — новые встречи появятся здесь.**
- [x] Empty registrations (no upcoming and no archive): **Пока нет регистраций** + **Откройте События и отметьтесь на встрече.**
- [x] Shared outline SVG icons live in one module if T-220/T-221 duplicated them; no icon-font package
- [x] `npm run lint` and `npm run build` pass in `apps/zarya-tg/frontend`

## Out of Scope

- EventCard structure and date headers (T-220)
- Circular RSVP / BackButton / details copy (T-221)
- Bottom tabs, MainButton, themeParams-as-brand
- Admin bot

## Implementation Notes

- Key files: `frontend/src/index.css`, `frontend/src/components/Header.tsx` + `.css`, `frontend/src/App.tsx` empty states, optional `frontend/src/components/icons.tsx`
- Count on the pill remains upcoming active registrations only (ADR-023)
- If T-220/T-221 already added some tokens, this ticket only fills gaps and dedupes — do not revert card/RSVP UI
- Verification is lint/build + visual smoke

## Verification

1. [x] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
2. [ ] Smoke: header toggle both directions; empty vs filled lists; light/dark
3. [ ] CI green on the PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/23
- Defaults chosen (if any): Home pill always shows the numeric count (including 0), matching the previous 🎫 badge. RSVP green/amber tokens are `#2d8a4e` / `#c4892a`.
- Residual risks: Light/dark visual smoke still needed.
