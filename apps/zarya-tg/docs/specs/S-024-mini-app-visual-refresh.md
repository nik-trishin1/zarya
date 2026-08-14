# S-024 — Mini App visual refresh (list + circular RSVP)

## Human summary (review this first)

**In plain language, we will:**
- Make event list cards look like a modern invite list (square photo, date and place with small icons, «Иду» / «Подумаю» on the photo) without hiding the list under a bigger poster
- Keep the current half-screen featured slider and keep featured events in the list underneath
- On the event page, replace the stack of wide buttons with two circles — «Буду» and «Подумаю» — plus a small «+1» chip next to «Буду» when guests are allowed
- Use the in-app 🏠 overlay on details (Telegram BackButton is not used after the 2026-08-14 prod incident); keep 🎫 / 🏠 on the existing toggle
- Fix leftover English strings to Russian

**We will not:**
- Show who else is going, add search/filters, maps, profiles, or a bottom tab bar
- Make posters larger, remove featured events from the list, or change the admin bot
- Add a third “не пойду” circle, Partiful glass bubbles, or Telegram’s big bottom MainButton (it would duplicate the circles)
- Change APIs, the database, or RSVP rules (`maybe` still does not take a seat)

**User-visible outcome:**
- Same app, same taps: open → see the slider and the full list → open an event → tap «Буду» or «Подумаю». It should look closer to Luma’s list and Partiful’s RSVP circles, still in Russian, still zarya colors.

**Main risks / open questions already decided:**
- Slider ~50vh; featured stay in the list (product, 2026-08-14)
- Two circles only; `+1` is a chip; cancel stays ghost text
- `BackButton` no (prod incident 2026-08-14); in-app 🏠; `MainButton` no
- Tokens keep `#e8874a` and paper/dark; green/amber only on RSVP chrome

**How we will know it worked (smoke):**
- Home: slider still ~half screen with list visible; a going event shows «Иду» on the thumb; a maybe event shows «Подумаю»
- Details: two circles; selecting «Буду» fills the circle and still registers; «+1» chip when allowed; archive has no circles
- Telegram back closes details; header «Мои» shows the count; no English “Stay tuned”

**Reviewer decision:** `[x] Approved for ticket split` · `[ ] Needs changes` · Reviewer: product · Date: 2026-08-14

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-024 |
| Title | Mini App visual refresh (list + circular RSVP) |
| Status | `done` |
| Related ADR / PRD | [ADR-024](../decisions/024-mini-app-visual-language.md), [ADR-002](../decisions/002-ux-navigation.md), [ADR-021](../decisions/021-home-featured-slider.md), [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md), [ADR-023](../decisions/023-past-events-archive.md), PRD US-2 / US-3 / US-4, [research](../research/event-app-redesign-benchmarks.md) |
| Owner | zarya maintainers |

## Problem

The Mini App already does the Jobs. Presentation lags event-app baselines: cards look like a settings list, details is a wall of equal buttons, navigation is emoji-only, and two English strings remain.

## Goals

- Luma-like compact list without growing the hero
- Partiful-like circular RSVP for existing `Буду` / `Подумаю` only
- Telegram `BackButton` caused a prod incident — keep 🏠; word labels on the ADR-002 toggle were reverted to 🎫 / 🏠 after product feedback
- Russian-only copy; keep brand colors
- Frontend-only; split into three tickets

## Non-goals

- Guest lists, avatars, comments, albums, host pages
- Categories, search, maps, ticketing chrome
- Bottom tabs, Create tab, admin Mini App / bot changes
- API, schema, RSVP state machine, capacity, maybe pings
- Enlarging slider or details cover; de-duplicating featured from the list
- Telegram `MainButton`; Partiful glass / floating host bar
- New npm icon/carousel libraries

## Proposed behavior

### Data / API

Unchanged. Trust existing `Event` fields (`is_registered`, `is_maybe`, `is_featured`, `party_size`, `allows_plus_one`, `allows_sharing`, `is_full`, `is_past`, seats).

### UI / bot copy (user-facing language)

**List / badges**
- Going overlay: **Иду**
- Maybe overlay: **Подумаю**
- Date header examples: **Сегодня / пт** · **Завтра / сб** · **28 июн / сб** (reuse `formatEventDate` weekday/date; do not invent a new locale)

**Details RSVP**
- Circle captions: **Буду** · **Подумаю**
- +1 chip: **+1** / **Убрать +1** (same meaning as today)
- Ghost cancel (going): **Отменить регистрацию**
- Ghost cancel (maybe): **Решил, что не пойду**
- Past, not going: **Событие прошло**
- Full, not going, not maybe: **Мест нет**
- Share / calendar: icon-only with `aria-label` **Поделиться** / **В календарь**

**Header**
- Home title: **События**
- Registrations title: **Мои регистрации**
- Toggle on home: **Мои** + count (count = upcoming `active` only, ADR-023)
- Toggle on registrations: **События**
- `aria-label` must stay descriptive (include count when on home)

**Empty**
- Home: **Нет предстоящих событий** + supporting line **Загляните позже — новые встречи появятся здесь.**
- Registrations (no upcoming and no archive): **Пока нет регистраций** + **Откройте События и отметьтесь на встрече.**

**Bot:** unchanged.

### Layout

**Home**

```text
┌─────────────────────────────────┐
│  События              [Мои  2]  │
├─────────────────────────────────┤
│  ▌ peek │████ POSTER ████│ peek ▐  ~50vh if featured
├─────────────────────────────────┤
│  Сегодня / пт                   │
│  [thumb Иду] title              │
│              clock  date-time   │
│              pin    location    │
│  [thumb    ] title …            │
└─────────────────────────────────┘
```

**Details (not archive)**

```text
┌─────────────────────────────────┐
│  cover ~200px                   │  in-app 🏠 (not Telegram BackButton)
│  Title                          │
│  🕒  date-time                  │
│  📍  location                   │  outline SVG, not emoji-in-copy
│  seats line                     │
│  description                    │
│                                 │
│    (✓) Буду     (⏸) Подумаю    │  circles; +1 chip under Буду
│    Отменить регистрацию         │  ghost, after going/maybe
│    (share) (calendar)           │  after going
└─────────────────────────────────┘
```

**Мои регистрации:** same cards; upcoming then **Архив**; no slider; no going/maybe overlay on archive thumbs.

### Errors and edge cases

| Case | Behavior |
|------|----------|
| 0 featured | List only; slider hidden (ADR-021) |
| Featured event | In slider **and** list |
| 1 calendar day in list | No date group header required |
| 2+ days | Headers above each group; order still API chronological |
| Going | Thumb **Иду**; details «Буду» filled; «Подумаю» hidden (ADR-022: no maybe while going) |
| Maybe | Thumb **Подумаю**; «Подумаю» filled; «Буду» available; no calendar/+1 until going |
| Full + not going | Circles: «Буду» disabled; «Подумаю» still allowed (ADR-022) |
| `allows_plus_one` false | No +1 chip; register party_size 1 only |
| Archive / `readOnly` | No circles, no +1, no share/calendar (ADR-023) |
| Deep link to event | Details opens; 🏠 closes to the list underneath |
| Outside Telegram | Same 🏠 control; same close handler |
| Missing cover | Existing `CoverImage` placeholder |

## Acceptance criteria (spec-level)

- [ ] ADR-024 proposed and linked from tickets
- [ ] Home slider height and featured-in-list unchanged
- [ ] Event cards use overlay status, icon meta, no corner emoji / `📍` paragraph
- [ ] Date headers when 2+ distinct days
- [ ] Details: two RSVP circles + +1 chip + ghost cancel; no MainButton
- [ ] In-app 🏠 closes details (Telegram `BackButton` is not used)
- [ ] Header toggle uses words + count
- [ ] English leftover strings gone
- [ ] No guest list, tabs, API/bot changes
- [ ] `npm run lint` and `npm run build` in `apps/zarya-tg/frontend` on implementing PRs

## Rollout / migration

Frontend-only CSS/React. No migration. Ship as three sequential PRs (T-220 → T-221 → T-222) or stacked on one branch if a single agent implements all after DoR.

## Open questions

None for behavior — defaults locked in ADR-024 / planning chat. **Human summary on this spec and on each ticket must be approved** before factory enqueue.
