# ADR-026: Optional event price (display-only)

**Date:** 2026-08-18  
**Status:** Proposed (implementation waits on spec/ticket Human summary approve)

## Context

Paid or “chip in” gatherings need a visible cost next to time and place. Organizers already collect money off-platform; the Mini App should answer «сколько», not charge cards.

Price is independent of approval ([ADR-025](025-manual-registration-approval.md)): a friendly hangout can show a ruble amount without a registration gate; a festival can use both.

Today event details list facts in equal secondary-grey rows (time → location → guests). A price in that chorus would be easy to miss.

## Decision

### 1. Not payments

No acquiring, invoices, «оплачено» status, or stored payment data. Rekvizity stay in the event description. Approval (if enabled) remains the human check that money arrived.

### 2. Schema

On `events`:

- `price_amount_minor` — `INTEGER NULL` (kopecks / cents). `NULL` = no price; do not render a price row. Do **not** use `0` in v1 (no «Бесплатно» label).
- `price_currency` — `CHAR(3) NULL`, ISO 4217. Set only together with the amount. Both null on existing rows.

Store **minor units from day one** so USD/EUR later do not need a migration. The pair is either both null or both set.

Mental model: **price per person**. UI shows a single formatted amount (no × `party_size`).

### 3. v1 admin: RUB, whole rubles

Create FSM: after **location**, before **description**:

- Prompt: **«Введите стоимость в рублях (например 1000) или нажмите «Без стоимости»»**
- Parse digits with spaces and an optional `₽`. Store `rubles * 100` and `price_currency = 'RUB'`.
- Reject negative / non-numeric; re-prompt.
- **«Без стоимости»** → both columns `NULL`.

**Edit may change price** (unlike `requires_approval` in v1), including reset via «Без стоимости».

USD/EUR pickers and fractional cents are **out of v1**. Formatter should still accept a currency code so later `$` / `€` can share it.

### 4. Display format

One formatter, used by API consumers, Mini App, and bot copy.

v1 RUB: `1 000 ₽` — thin/narrow non-breaking space as thousands separator, `₽` after the number. Not `1000 руб.`, not `₽1000`.

Later (not this ADR’s tickets): `1 000 $`, `1 000 €` (amount then symbol, RU-familiar order).

API may expose raw `price_amount_minor` + `price_currency` plus a preformatted `price_label` (or the client formats with the same rules). Prefer a shared backend helper so bot announcements never drift from the Mini App.

### 5. Where it appears

- **Event details:** if set, a fact row **after location, before guests**: time → location → **price** → guests.
- **List `EventCard`:** third meta line **only when set** (free cards stay two-line). Same formatter. Not on the poster slider (ADR-021; too little overlay space).
- **Create confirm + ADR-011 announcement:** price line after location when set.
- Archive / past details: show the stored price if present (read-only).

### 6. Fact-row emphasis (ADR-024 addendum)

Accent **the whole details fact block**, not only price:

- Values: `--color-text-primary`, `font-weight: 500`
- Icons: `--color-accent` (`#e8874a`)
- Block: light `--color-card` padding so facts separate from the description
- Price row: same + `font-weight: 600` and `font-variant-numeric: tabular-nums`

List-card meta stays caption-sized (Luma density); if a price line exists, meta icons are slightly less transparent than today.

Do **not**: red sale color, struck-through “old” price, «Платно» badge on the cover, emoji in Mini App fact rows. New outline `IconTag` (or banknote) in the existing SVG set.

RSVP green/amber remain RSVP-only (ADR-024).

## Alternatives considered

**Free-text price on the event.** Rejected — blocks later currencies and consistent formatting.

**Major-unit integer only (rubles).** Rejected for storage — cents would force a later migration. Admin v1 still types whole rubles.

**Show «Бесплатно» when null.** Rejected — most events are free; extra noise.

**Multiply by party_size in the UI.** Rejected — display-only per-person amount; admin already sees `party_size` on applications.

**Price on the home poster slider.** Rejected — overlay already has date + name.

## Consequences

- Event JSON grows two nullable fields (and a label if centralized).
- ADR-011 announcement template gains an optional price line.
- ADR-024 details fact order and weight change; list cards may grow a third meta line.
- Spec: [S-215](../specs/S-215-event-price.md). Ticket: [T-215](../tickets/T-215-event-price.md).
