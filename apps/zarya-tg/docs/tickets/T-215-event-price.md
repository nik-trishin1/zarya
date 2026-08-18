# T-215 — Event price (display) + fact-row emphasis


## Human summary (review this first)

**Will do:**
- Optional event price, shown as **1 000 ₽**, after place and before guest count
- Admin sets or clears it on create and edit («Без стоимости»)
- Same string in the Mini App, bot preview, and new-event announcement
- Make the details fact block (time, place, price, guests) more visible; price slightly bolder
- List cards get a third meta line only when a price exists

**Will not do:**
- Payments, «оплачено», or «Бесплатно» when empty
- Multiply by +1; USD/EUR picker (store currency code anyway)
- Price on the poster slider
- Registration-approval work (T-213 / T-214)

**Touched areas:** event DB/API, admin create/edit FSM, announcements, Mini App details + list cards, fact-row CSS

**Risk:** Low–medium — formatter/bot/Mini App must not drift; do not write currency without amount

**Smoke check after merge:** Create `1000` → details and card show `1 000 ₽` between place and guests; announce has the line after place; «Без стоимости» hides it; edit can change or clear; fact icons use accent color

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____  
**DoR:** `[ ] Not ready` — Human summary + S-215 must be approved first

---

| Field | Value |
|-------|-------|
| ID | T-215 |
| Title | Optional event price + fact-row emphasis |
| Status | `todo` |
| Spec / ADR | [S-215](../specs/S-215-event-price.md), [ADR-026](../decisions/026-event-price.md); ADR-011 / ADR-024 addenda |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Show an optional per-person ruble price consistently, and make event facts on the details screen easier to scan.

## Acceptance criteria

- [ ] `price_amount_minor` + `price_currency` nullable; both null or both set; amount > 0; `schema_updates` for existing DBs
- [ ] Create FSM: after location, before description; parse `1000` / `1 000` / `1000₽` as 100000 minor RUB; «Без стоимости» → null/null
- [ ] Edit can change or clear price; confirm preview shows formatter output
- [ ] Shared `format_event_price` → `1 000 ₽` (narrow/nbsp thousands, symbol after); `EventResponse.price_label` null when unset
- [ ] ADR-011 announcement inserts the formatted line after location iff set
- [ ] Mini App details: time → location → price → guests; `IconTag` outline; hide price row when null
- [ ] List `EventCard`: third meta line iff price; poster slider unchanged
- [ ] Details `.event-details__rows`: card padding, primary values, accent icons, price weight 600 + tabular-nums
- [ ] No «Бесплатно», no payment fields
- [ ] Backend parse/format/create/edit tests; `npm run lint && npm run build`

## Out of scope

- T-213 / T-214
- USD/EUR UI, cents, «за человека» caption
- Sale/red badges; slider overlay price

## Implementation notes (for agents)

- Key files: `backend/app/models/event.py`, `schema_updates.py`, `schemas/event.py`, `services/events.py`, `utils/formatting.py` (or new `pricing.py`), `bot/handlers.py`, `bot/keyboards.py`, `bot/states.py`, announcement builder, `frontend/src/api/client.ts`, `EventDetails.tsx` + css, `EventCard.tsx` + css, `components/icons.tsx`
- Constraint: never persist currency without amount (and vice versa)
- Independent of approval; can merge without T-213
- Thousands separator: prefer U+202F or NBSP so `1 000 ₽` does not wrap between digits

## Verification (agents)

1. [ ] `PYTHONPATH=. pytest -q` in `apps/zarya-tg/backend`
2. [ ] `npm run lint && npm run build` in `apps/zarya-tg/frontend`
3. [ ] CI green on the PR
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](../../../../process/ai-factory/REVIEW_PASS.md))

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
