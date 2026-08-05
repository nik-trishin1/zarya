# ADR-021: Home featured poster slider

**Date:** 2026-08-05
**Status:** Accepted

## Context

With few upcoming events, the home screen (list-only cards per ADR-002 / PRD US-2) underuses cover art. Product wants a large poster slider (~half the viewport) above the existing list so featured events are visually prominent. Events remain subject to access-group visibility (ADR-020): users must only see posters for events they can already see in the list.

Requirements for this iteration:

1. Only **admin-marked** events appear in the slider (not every upcoming event).
2. Marking uses the **existing** Telegram admin create/edit FSM — no separate admin Mini App or new bot menu.
3. The list under the slider stays as today’s `EventCard` layout.
4. Slider and list share the same visibility rules (public / group membership / admin bypass).

## Decision

### Schema

- Column `events.is_featured` — `BOOLEAN NOT NULL DEFAULT FALSE`.
- Existing rows stay non-featured until an admin opts in.

### Visibility and API

- Continue to use a single authenticated `GET /api/events` that returns upcoming events after `_filter_visible_events` (ADR-020).
- Expose `is_featured` on `EventResponse` (and detail responses that reuse the same schema).
- **No** separate featured-only endpoint. The Mini App builds the slider by filtering `is_featured === true` from the already ACL-filtered list.
- Chronological order (`date`, `time`) applies to both list and slider subset.
- Past events remain hidden from active UI (ADR-018); a featured past event does not appear.

### Home UI

- When the filtered list contains at least one featured event, show a poster slider (~50vh) above the event list.
- Each slide shows cover art (or existing placeholder), overlay **date-time** and **name** (Russian formatting already used on cards). Tap opens the same event details flow as a list card.
- Zero featured → list only (current home). Zero upcoming after ACL → existing empty copy; no slider.
- One featured → single poster (no swipe chrome / dots). Multiple → horizontal CSS `scroll-snap` carousel; no autoplay; no new carousel dependency.
- «Мои регистрации» has no slider. List card design is unchanged (location and ✅ stay on cards only).

### Admin bot

- Create FSM: after audience, ask «Показать в слайдере на главной?» with Да / Нет; default path is Нет (`is_featured=false`).
- Edit FSM: allow changing `is_featured` (Yes / No / Оставить), even though edit still does not change audience or capacity.
- Confirm summaries show whether the event is featured.

### Relationship to ADR-002

Home still opens directly to event discovery (no splash). The slider is an additional discovery surface on the same screen, not a separate menu. Critical path remains: open app → tap event → register.

## Alternatives considered

**Put all upcoming events in the slider.** Rejected — with growth the hero would become noisy; admin curation keeps the surface intentional while event count is small.

**Separate featured API.** Rejected — duplicates ACL and ordering; client filter on the existing list is enough.

**Separate admin UI / bot menu for featured.** Rejected — product asked to reuse create/edit only.

**Client-side group filtering for the slider.** Rejected — ACL must stay server-side (ADR-020); the list response is already filtered.

## Consequences

- Admins must explicitly mark events for the hero; unmarked events only appear in the list.
- Edit gains one new field (`is_featured`) while audience/capacity edit remain out of scope (unchanged from ADR-012 / ADR-020).
- Spec / tickets: S-209, T-209 (backend + bot), T-210 (frontend).
- PRD US-2 wireframe (list-only home) is extended by this ADR; list card AC remain valid.
