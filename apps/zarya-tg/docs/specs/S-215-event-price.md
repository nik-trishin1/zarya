# S-215 — Optional event price + fact-row emphasis

## Human summary (review this first)

**In plain language, we will:**
- Let the admin optionally set a price when creating or editing an event (skip = no price shown)
- Show the amount as **1 000 ₽** after time and place, before the guest count, so it is obvious what the gathering costs
- Make the whole fact block on the event page a bit stronger (not grey-on-grey) so price, time, and place do not slip past the eye
- If a list card has a price, show it as a third small line; free events stay as they are
- Put the same formatted amount in the bot preview and in the «new event» announcement

**We will not:**
- Take payments, mark anyone as paid, or multiply the price by +1 in the app
- Print «Бесплатно» when there is no price
- Let the admin pick dollars or euros yet (the database will already store a currency code)
- Put the price on the home poster slider

**User-visible outcome:**
- Paid events show **1 000 ₽** in a clear fact block; free events look like today plus slightly stronger time/place/guest rows.

**Main risks / open questions already decided:**
- Display-only; not acquiring (ADR-026)
- Per person; one amount in the UI
- v1 RUB whole rubles; stored as minor units + ISO code
- Null pair = hide the row
- Price is editable after create; approval flag is not (separate spec)

**How we will know it worked (smoke):**
- Create with `1000` → details order: date → place → **1 000 ₽** → guests; list card has a third line; announce includes the amount after place
- Create «Без стоимости» → no price row anywhere
- Edit to 2 500 ₽ then «Без стоимости» → UI and announce-style preview follow
- Fact block on details uses primary text and accent icons; price row is slightly bolder

**Reviewer decision:** `[ ] Approved for ticket split` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-215 |
| Title | Optional event price + fact-row emphasis |
| Status | `draft` |
| Related ADR / PRD | [ADR-026](../decisions/026-event-price.md); [ADR-011](../decisions/011-new-event-announcement.md); [ADR-024](../decisions/024-mini-app-visual-language.md). Independent of [S-213](S-213-manual-registration-approval.md). |
| Owner | zarya maintainers |

## Problem

Cost lives in the description (or nowhere), so it is easy to miss. Details facts are secondary-grey and equal-weight. Organizers need a first-class optional amount without building payments.

## Goals

- Optional structured price on all events
- Canonical RU format `1 000 ₽`
- Details fact order: time → location → price → guests
- Stronger fact block; price slightly heavier
- List card third line only when set
- Bot create/edit + ADR-011 announcement use the same formatter

## Non-goals

- Acquiring, invoices, paid status
- «Бесплатно» label
- × `party_size` in UI
- USD/EUR admin UI (column exists)
- Price on poster slider
- Red/sale chrome

## Proposed behavior

### Data / API

- `events.price_amount_minor INTEGER NULL`
- `events.price_currency CHAR(3) NULL` (ISO 4217)
- Check/constraint: both null **or** both non-null; amount `> 0` in v1
- `create_event` / `update_event` accept the pair; `None`/`None` clears on edit
- `EventResponse`: `price_amount_minor`, `price_currency`, and `price_label` (`"1 000 ₽"` or `null`) so Mini App and tests share one formatter
- Shared helper e.g. `format_event_price(amount_minor, currency) -> str | None`

**v1 write path:** currency always `RUB` when amount set. Admin types whole rubles; store `rubles * 100`.

**Parse (bot):** strip spaces and `₽`/`руб`; integer `≥ 1`; typical max e.g. 10_000_000 rubles (reject absurd).

### UI / bot copy (user-facing language)

**Create:** after location, before description:

> Введите стоимость в рублях (например 1000) или нажмите «Без стоимости»

Button **«Без стоимости»**. Confirm preview: formatted price after `📍`, or omit.

**Edit:** show current price (or «не указана»); same prompt; «Оставить» / «Без стоимости» / new number.

**Mini App details:** if `price_label`, row with `IconTag` (outline, same stroke set) + label, between pin and guests.

**Mini App list:** if `price_label`, third `event-card__meta-row`.

**Announcement (ADR-011):** after location, the formatted amount only (no extra «Стоимость:» prefix required; symbol is enough). Omit when null.

### Fact-row emphasis

`.event-details__rows`:

- Card-like padding/background `--color-card`
- Value color `--color-text-primary`, weight 500
- Icons `--color-accent`
- Price row extra: weight 600, `font-variant-numeric: tabular-nums`

List meta stays caption size; when a price line exists, icon opacity closer to 1.

Applies even when price is absent (time/place/guests still stronger).

### Errors and edge cases

- `1000`, `1 000`, `1000₽` → same store/display
- `0`, negative, letters → re-prompt
- Null price + currency leftover forbidden (service always writes the pair)
- Archive details: still show price if stored
- Missing fields on old API clients: treat as no price

## Acceptance criteria (spec-level)

- [ ] Columns + schema_updates; existing events null/null
- [ ] Create/edit persist and clear price
- [ ] Formatter: 100000 minor RUB → `1 000 ₽` (nbsp thousands)
- [ ] Details order time → location → price → guests; hidden when null
- [ ] List third line only when set; slider unchanged
- [ ] Announcement and create confirm include/omit correctly
- [ ] Details fact block restyle as specified
- [ ] No payment fields or «Бесплатно»
- [ ] Backend parse/format tests; frontend lint/build

## Rollout / migration

- Additive nullable columns
- Independent of S-213; can ship T-215 alone

## Open questions

> None. Deferred: USD/EUR picker; fractional cents; «за человека» caption.

---

**Ticket:** [T-215](../tickets/T-215-event-price.md)
