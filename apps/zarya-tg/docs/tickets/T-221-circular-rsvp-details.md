# T-221 — Mini App: circular RSVP + details chrome


## Human summary (review this first)

**Will do:**
- On the event page, replace the wide «Буду» / «Подумаю» / «Буду +1» stack with two circles (icon + caption) and a small «+1» chip under «Буду» when +1 is allowed
- Use Telegram BackButton instead of the 🏠 overlay; keep cancel as ghost text; share/calendar as small icon buttons after going
- Russian copy for past/full states (no “Stay tuned”)

**Will not do:**
- Home card restyle or header «Мои» label (T-220 / T-222)
- A third “не пойду” circle, Partiful glass, Telegram MainButton, guest list
- Backend, bot, or RSVP rule changes (maybe still does not take a seat)

**Touched areas:** Mini App `EventDetails`, Telegram WebApp BackButton + haptic

**Risk:** Medium — easy to break +1 / maybe / full / archive transitions if the new controls skip existing handlers

**Smoke check after merge:**
- Not going: two circles; «Подумаю» does not take a seat; «Буду» registers
- +1 chip only when `allows_plus_one` and going (or registering with +1 as today)
- Archive event: no circles; Telegram back (or chevron outside Telegram) closes details
- No English “Stay tuned” / “Fully booked”
- Frontend lint/build pass

**Reviewer decision:** `[x] Approved to implement` · `[ ] Needs changes` · Reviewer: product · Date: 2026-08-14  
**DoR:** `[x] Approved` — Human summary approved with S-024 / ADR-024 (implement request 2026-08-14)

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-221 |
| Title | Circular RSVP + event details chrome |
| Status | `in_review` |
| Spec / ADR | [S-024](../specs/S-024-mini-app-visual-refresh.md), [ADR-024](../decisions/024-mini-app-visual-language.md), [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md), [ADR-019](../decisions/019-registration-party-size.md), [ADR-023](../decisions/023-past-events-archive.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Make RSVP scannable (two circles) without changing registration semantics or adding a competing MainButton.

## Acceptance Criteria

- [x] Details cover stays ~200px; body uses icon rows for date/time, location, seats (`formatEventSeats`); description unchanged in meaning
- [x] RSVP: two ~56px circles **Буду** (check) and **Подумаю** (pause) + captions; selected = filled semantic color; unselected = outline
- [x] `+1` is a chip under/beside **Буду** when `allows_plus_one`; never a third circle; same enable/disable rules as today’s «Буду +1» / «Добавить +1» / «Убрать +1»
- [x] No maybe circle while already going (ADR-022); maybe allowed when full; «Буду» disabled when full / past / cannot take seats
- [x] Cancel remains ghost: **Отменить регистрацию** / **Решил, что не пойду** — no Can't-go circle
- [x] After going: share + calendar as small circular icon buttons with Russian `aria-label`; hidden when sharing disallowed / archive
- [x] `readOnly` archive: no RSVP circles, no +1, no share/calendar
- [x] Telegram `BackButton` shown while details open and hides the 🏠 overlay; outside Telegram, chevron back uses the same `onClose`; haptic on RSVP taps; **no** `MainButton`
- [x] Copy: **Событие прошло** · **Мест нет** (replace English Stay tuned / Fully booked)
- [x] `npm run lint` and `npm run build` pass in `apps/zarya-tg/frontend`

## Out of Scope

- EventCard / slider / date headers (T-220)
- Header «Мои» / empty-state rewrite (T-222)
- Guest list, glass, MainButton, bot/API
- Changing maybe ping or capacity logic

## Implementation Notes

- Key files: `frontend/src/components/EventDetails.tsx` + `.css`, `frontend/src/hooks/useTelegram.ts` (BackButton show/hide on mount/unmount)
- Reuse existing `registerForEvent` / `markEventMaybe` / `cancelRegistration` / `updateRegistrationPartySize` / `downloadCalendar` / share helpers
- Hide BackButton in `onClose` and on unmount so home does not keep a native back control
- Icons: extend `components/icons.tsx` from T-220 or add locally and let T-222 dedupe
- Suggested tests: none beyond lint/build; keep handlers identical so existing API contracts hold

## Verification

1. [x] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
2. [ ] Smoke: going / +1 / maybe / clear maybe / full / past / archive / share / calendar / back
3. [ ] CI green on the PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/23
- Defaults chosen (if any): `+1` chip still registers `party_size` 2 from unregistered/maybe (same as today’s «Буду +1»). Calendar/share only after going. Filled «Буду» / «Подумаю» circles replace the old registered banners.
- Residual risks: BackButton/haptic need a real Telegram client; `MainButton` is unused.
