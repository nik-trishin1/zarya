# S-209 — Home poster slider (featured events)

## Human summary (review this first)

**In plain language, we will:**
- Add a large poster slider on the Mini App home screen (~half the screen height) for events the admin marks as featured
- Show date-time and event name on each poster; tapping opens that event’s details
- Keep the current event list under the slider unchanged
- Let admins set the featured flag in the existing Telegram bot create and edit flows (no new admin screen)
- Only show posters the user is allowed to see (same group rules as the event list)

**We will not:**
- Build a separate admin UI or featured-management menu
- Put every event in the slider by default
- Add Platinumlist-style search, filter chips, or video in the hero
- Change how list cards look (cover thumbnail, location, ✅ stay on the list)
- Show group-restricted events to users who are not members (or non-admins)

**User-visible outcome:**
- Home: optional featured poster carousel above the familiar event list; empty/non-featured homes look like today

**Main risks / open questions already decided:**
- Flag is `is_featured` (default false); slider built from the same `GET /api/events` response after ACL
- No autoplay; CSS scroll-snap only; chronological order among featured
- Edit can toggle featured; audience/capacity still not editable on edit

**How we will know it worked (smoke):**
- Create a public featured event → appears in slider and list for a normal user
- Create a Core featured event → only Core members and admins see it in slider/list
- Clear featured on edit → slider hides when none remain; list still shows the event
- Zero featured → home is list-only as today

**Reviewer decision:** `[ ] Approved for ticket split` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-209 |
| Title | Home poster slider (featured events) |
| Status | `draft` |
| Related ADR / PRD | [ADR-021](../decisions/021-home-featured-slider.md), [ADR-020](../decisions/020-access-groups.md), [ADR-002](../decisions/002-ux-navigation.md), [ADR-018](../decisions/018-hide-past-events.md), PRD US-2 |
| Owner | zarya maintainers |

## Problem

With few upcoming events, the list-only home underuses cover images. Users should discover highlighted events via large posters without losing the existing list or breaking access-group visibility.

## Goals

- Featured poster slider (~50vh) on home when at least one visible featured event exists
- Overlay date-time + name; tap → event details (same as list)
- Admin marks featured via bot create/edit FSM
- ACL identical to list (ADR-020); no client-side group filtering
- Preserve current `EventCard` list and registrations screen

## Non-goals

- Separate featured API or admin Mini App
- Search, date chips, categories, video/mute controls
- Autoplay carousel library dependency
- Changing list card layout or putting location/✅ on posters
- Editing audience or capacity in the edit flow (unchanged)
- Showing past featured events (ADR-018)

## Proposed behavior

### Data / API

- Column `events.is_featured BOOLEAN NOT NULL DEFAULT FALSE` (startup `schema_updates`).
- `create_event` / `update_event` accept `is_featured`.
- `EventResponse` includes `is_featured`.
- `GET /api/events` unchanged aside from the new field; still upcoming + `_filter_visible_events`.
- Mini App: `featured = events.filter(e => e.is_featured)`; hide slider when empty.

### UI / bot copy (user-facing language)

**Mini App (Russian):**
- Poster overlay uses existing `formatEventDate` (e.g. `Пн, 5 авг, 19:00`) and `event.name`.
- Slider `aria-label` / button labels in Russian (e.g. open event by name).
- Empty state unchanged: «Нет предстоящих событий».

**Admin bot (Russian):**
- Prompt: «Показать в слайдере на главной?»
- Buttons: «Да» / «Нет» (create); edit also «Оставить» with current value shown.
- Confirm summary includes a featured line (e.g. «Слайдер: да» / «Слайдер: нет»).

### Layout (home)

```text
┌─────────────────────────────────┐
│  [🎫]          События          │
├─────────────────────────────────┤
│  ▌ peek │████ POSTER ████│ peek ▐  ~50vh (if any featured)
│         │ date-time             │
│         │ event name            │
├─────────────────────────────────┤
│  EventCard list (unchanged)     │
└─────────────────────────────────┘
```

### Errors and edge cases

| Case | Behavior |
|------|----------|
| 0 upcoming after ACL | Empty state; no slider |
| Upcoming but 0 featured | List only |
| 1 featured | Single poster; no dots/swipe chrome |
| N featured | Horizontal snap carousel; dots optional; order by date/time |
| Featured + group audience, non-member | Absent from API → absent from slider and list |
| Admin | Sees all groups’ featured posters |
| Featured + past | Hidden by upcoming filter |
| Missing/broken cover | Existing `CoverImage` placeholder |
| Deep link / registrations | Unchanged; no slider on registrations |

## Acceptance criteria (spec-level)

- [ ] ADR-021 documented and linked from tickets
- [ ] Backend persists and returns `is_featured`; default false
- [ ] Admin create and edit can set featured; confirm shows status
- [ ] Home shows slider only for ACL-visible featured upcoming events
- [ ] Poster shows date-time + name; tap opens details
- [ ] Event list under slider unchanged; registrations unchanged
- [ ] Group visibility matches list (member / public / admin)
- [ ] Tests cover persist + visibility; frontend lint/build pass when T-210 lands

## Rollout / migration

- Additive column with default `false`; no data backfill required.
- Deploy backend before or with frontend that reads `is_featured` (frontend treats missing as false).

## Open questions

None — defaults locked in ADR-021 / planning chat (chronological featured, no autoplay, edit toggles featured, client filter on list response).
