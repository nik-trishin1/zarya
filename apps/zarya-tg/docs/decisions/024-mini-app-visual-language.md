# ADR-024: Mini App visual language (list + circular RSVP)

**Date:** 2026-08-14  
**Status:** Proposed

## Context

The Mini App already delivers the MVP Jobs (browse upcoming events, RSVP, my registrations, archive). Visual chrome still looks like an early settings list: 80×80 thumbs with corner emoji, `📍` meta, a stack of equal-weight buttons on details, and 🎫/🏠-only navigation. Event apps on the market (Mobbin: Luma, Partiful, Locals) use a denser list language and a clearer RSVP control without requiring guest lists or a discovery marketplace.

Product constraints from planning (2026-08-14):

- Do **not** enlarge the home featured slider. Current ~50vh is correct because the **full list stays visible underneath**.
- Featured events remain in the list (no de-duplication vs ADR-021).
- Details cover stays medium (~200px), not a second hero.
- Restyle existing RSVP (`Буду` / `Подумаю`) as Partiful-style **circles** (icon + caption). Do not add a third “Can't go” circle or Partiful glass/bubbles.
- This is presentation only — not a new Segment+Job and not an MVP expansion.

Research: [event-app-redesign-benchmarks.md](../research/event-app-redesign-benchmarks.md). Spec: [S-024](../specs/S-024-mini-app-visual-refresh.md).

## Decision

### 1. Scope

Visual and IA refresh of the existing three surfaces: home, event details, «Мои регистрации» (including Архив). **No** backend/schema/API change. **No** admin bot change.

### 2. Home slider (ADR-021 unchanged except card restyle)

- Slider height remains ~50vh; peek of adjacent slides and list immediately below — unchanged.
- Featured events **continue to appear in the list**.
- ADR-021’s “list card design is unchanged” is **superseded for card chrome only** (thumb, meta, status). Slider behavior, `is_featured`, and ACL are unchanged.

### 3. List language (Luma row)

Each `EventCard` (home and «Мои регистрации»):

- ~80px rounded-square cover (same order of size as today; not 16:9 full-width posters).
- Status overlay **on the thumb**, bottom-left: **«Иду»** (going) or **«Подумаю»** (maybe). No corner ✅ / … emoji.
- Bold title; two meta lines with outline icons: date/time (clock), location (pin). No `📍` prefix.
- Optional date group headers when the upcoming list has **2+ distinct calendar days**: `Сегодня / пт` (or `D MMM / weekday`) using existing Russian date formatting.

Archive cards stay muted (ADR-023); they do not show going/maybe overlays.

### 4. Event details

- Cover remains ~200px full-width (not ~40vh).
- Telegram **`BackButton`** closes details; hide the custom 🏠 overlay.
- Title, then icon rows: date/time, location, seats (`formatEventSeats`). Then description.
- **RSVP row:** two circles (~56px hit target) with icon + caption:
  - **«Буду»** — check icon
  - **«Подумаю»** — pause icon
  - Selected = filled semantic color (going green / maybe amber). Unselected = outline on card surface.
  - Calm icons only — not Partiful bandage/broken-heart toys.
- **`+1` is not a third circle.** When `allows_plus_one`, a compact chip under/beside **«Буду»** (add / remove +1 as today).
- No “Can't go” circle. Cancel stays ghost text: **«Отменить регистрацию»** / **«Решил, что не пойду»**.
- After going: share and calendar as small circular icon buttons (not equal-weight full-width buttons).
- Archive / read-only: no RSVP circles (ADR-023).
- **Do not** use Telegram `MainButton` for RSVP (duplicates the circle row). Haptic feedback on RSVP taps is in scope.
- Replace English leftovers (`Fully booked. Stay tuned!`, `Stay tuned!`) with Russian.

### 5. Navigation chrome (ADR-002 addendum)

- Keep the **single toggle** (no bottom tab bar). Two screens still do not justify tabs.
- Add **text** on the control: home shows **«Мои»** plus the upcoming-registration count; registrations shows **«События»**. Emoji-only 🎫/🏠 is not required; a short word is enough.
- Home title stays **«События»**; registrations title stays **«Мои регистрации»**.

### 6. Tokens

- Keep brand accent `#e8874a` and the warm paper / dark pair in `index.css`.
- Add a type scale (title / meta / body).
- RSVP semantic green / amber are **only** for badges and selected circles — not as brand fill.
- Inline SVG strokes (~20px). No new icon-font dependency.

### 7. Empty states

Icon + two-line Russian copy (Luma-style). Home: keep the meaning of «Нет предстоящих событий». Registrations: keep the meaning of «Вы не зарегистрированы ни на какие события». Slightly warmer supporting line allowed in S-024.

## Alternatives considered

**Enlarge home hero / hide featured from the list.** Rejected — product: the peek of the full list is the point of the current slider.

**Telegram MainButton as primary RSVP.** Rejected — would compete with the circular row.

**Three Partiful circles including Can't go.** Rejected — cancel stays a lower-weight ghost action; `+1` is a chip, not a circle.

**Bottom tab bar.** Rejected — still only two user screens (ADR-002).

**Guest list / avatars.** Rejected — PRD privacy; Partiful’s core Job, not ours.

## Consequences

- ADR-021 list-card freeze is lifted for presentation; slider height and featured-in-list stay.
- ADR-002 toggle stays; labels become words.
- Implementation is frontend-only, split in S-024 tickets (home cards, details RSVP, tokens/chrome).
- Human summary on the spec/tickets must be approved before factory enqueue (DoR).
