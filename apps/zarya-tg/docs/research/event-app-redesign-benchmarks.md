# Event-app redesign benchmarks (zarya Mini App)

> Research input for [ADR-024](../decisions/024-mini-app-visual-language.md) and [S-024](../specs/S-024-mini-app-visual-refresh.md).  
> Not a product decision by itself. Steal **components**, not competitor Jobs.

**Date:** 2026-08-14  
**Sources:** Mobbin paid MCP (Partiful, Luma, Locals iOS) + current Mini App UI.

## Human summary

zarya stays a small-circle Telegram Mini App: open → see events → RSVP in two taps. We should look more like **Luma’s compact list** (scan many events, list always visible under the existing ~50vh slider) and use **Partiful’s circular RSVP** only as a restyle of today’s `Буду` / `Подумаю`. We should not copy guest lists, city discovery, glassmorphism, or larger cover heroes.

## What this is not

This is not a new Segment+Job bet and not an MVP expansion. Out of scope vs PRD / ADRs: participant lists, profiles, comments, photo albums, categories/search, maps, public city feeds, a Create tab, bottom navigation.

## Benchmarks (Mobbin)

| App | Role vs zarya | Primary flows / screens |
|-----|----------------|-------------------------|
| **Luma** | Visual analog already in the PRD — editorial, quiet chrome, high list density | [Home](https://mobbin.com/flows/7a18b76f-0c17-415c-9b04-ac4300bcd28b) · [Your Events](https://mobbin.com/screens/7c41a229-878f-4341-b21b-76b4df6308d0) · [list row](https://mobbin.com/screens/331782b6-d487-4d7f-8842-92cd9ba9de27) · [invited detail](https://mobbin.com/flows/1e6b6523-dbe1-46a6-8c1a-cc96193e345c) · [past empty](https://mobbin.com/flows/c586de98-8652-4177-a130-dfaf01fce50d) |
| **Partiful** | Closest Job (private invite RSVP) — party chrome is optional | [Event detail](https://mobbin.com/flows/eec6cdc4-0b7c-4d8c-92c7-825a2121599d) · [home](https://mobbin.com/screens/fb703a16-de4f-42c9-b8df-d7c135d0e5ff) · [circular RSVP](https://mobbin.com/screens/301b1252-7ce0-4a4a-b2ab-8263ed634515) |
| **Locals** | Club OS — take icon-row structure only | [search → details](https://mobbin.com/flows/76de58e2-7d23-40fd-820b-f469873b2100) |

Related screens (component language, not product model): [Posh RSVP pill](https://mobbin.com/screens/e845ea47-0920-44bd-9949-6db52575e5b9), [Amie RSVP chip](https://mobbin.com/screens/5b0e8074-11ab-463f-8284-4e199953a3a1). Nextdoor/Discord event UIs appeared in adjacent Mobbin results; do not treat them as zarya analogs.

## Steal vs refuse

| Pattern | Source | Decision |
|---------|--------|----------|
| Home = events immediately, no splash | Luma, Partiful, zarya ADR-002 | **Keep** |
| Featured slider ~50vh with list peeking below | zarya ADR-021 | **Keep height.** Do not enlarge toward a full-screen hero. Featured events **stay in the list**. |
| Compact row: square thumb, bold title, outline clock/pin | [Luma list](https://mobbin.com/screens/331782b6-d487-4d7f-8842-92cd9ba9de27) | **Steal** — primary list language |
| Date group headers `Today / Friday` | Luma | **Steal** → `Сегодня / пт` |
| Status badge on the thumbnail | [Luma Your Events](https://mobbin.com/screens/7c41a229-878f-4341-b21b-76b4df6308d0) | **Steal** — `Иду` / `Подумаю` overlay; replace corner ✅ / … |
| Icon meta rows (date, place, seats) | [Locals details](https://mobbin.com/flows/76de58e2-7d23-40fd-820b-f469873b2100) | **Steal** |
| Circular RSVP: icon in ~56px circle + caption | [Partiful](https://mobbin.com/screens/301b1252-7ce0-4a4a-b2ab-8263ed634515) | **Steal, scoped** — only `Буду` / `Подумаю`. Calm icons (check / pause), not bandage/broken hearts |
| `+1` as a third circle | — | **Refuse** — chip under/beside `Буду` |
| Third “Can't go” circle | Partiful | **Refuse** — ghost text cancel as today |
| Glass bubbles, floating host toolbar, activity feed | Partiful | **Refuse** |
| Guest avatars / who is going | Partiful, Luma, Locals | **Refuse** (PRD privacy) |
| Bottom tabs / Create tab | Luma, Locals, Partiful | **Refuse** (ADR-002; admin stays in the bot) |
| 55–80% club/event heroes | Locals, some Partiful pages | **Refuse** — details cover stays ~200px |
| Price / waitlist / sold-out chrome | Luma | **Refuse** (no ticketing) |
| Telegram `BackButton` | Mini App host | **Steal** — replace custom 🏠 on details |
| Telegram `MainButton` as RSVP | Mini App host | **Refuse for this pass** — would duplicate the circle row |
| Haptic on RSVP tap | Mini App host | **Steal** |

## Reusable component inventory (for S-024)

Map to existing files; no new backend.

| Primitive | Target | Notes |
|-----------|--------|--------|
| Featured slider | [`PosterSlider`](../../frontend/src/components/PosterSlider.tsx) | Height ~50vh unchanged |
| Event row | [`EventCard`](../../frontend/src/components/EventCard.tsx) | 80px rounded thumb; overlay badge; title; two icon meta lines |
| Date section header | [`App.tsx`](../../frontend/src/App.tsx) | Group upcoming list when 2+ distinct days |
| Circular RSVP | [`EventDetails`](../../frontend/src/components/EventDetails.tsx) | Two circles; selected fill (going green / maybe amber); outline unselected |
| `+1` chip | EventDetails | Only if `allows_plus_one`; not a circle |
| Icon rows | EventDetails | Date/time, location, seats (`formatEventSeats`) |
| Share / calendar | EventDetails | Small circular icon buttons after going |
| Back | EventDetails + Telegram SDK | `BackButton`; hide 🏠 overlay |
| Header toggle | [`Header`](../../frontend/src/components/Header.tsx) | Keep single control (ADR-002); add words (`Мои` + count) |
| Empty state | Home / registrations | Icon + two-line Russian copy |
| Tokens | [`index.css`](../../frontend/src/index.css) | Keep `#e8874a` + paper/dark; type scale; RSVP colors **only** on badges/circles |
| Icons | New small SVG set | Clock, pin, check, pause, share, calendar, chevron — inline strokes ~20px; no icon font |

## Gaps vs current UI

- List cards read as a settings list (emoji status, `📍` in a paragraph).
- Details is a wall of equal-weight buttons (`Буду`, `Буду +1`, `Подумаю`, calendar, share, cancel).
- English leftovers: `Fully booked. Stay tuned!`, `Stay tuned!`
- Navigation is emoji-only (🎫 / 🏠); Telegram `BackButton` unused.

## Defaults locked in planning (2026-08-14)

- Visual/IA only; no API/schema change.
- Slider height and list membership unchanged vs ADR-021.
- Two RSVP circles only; `+1` chip; cancel ghost.
- No `MainButton`; yes `BackButton` + haptic.
- Russian-only (ADR-003).
