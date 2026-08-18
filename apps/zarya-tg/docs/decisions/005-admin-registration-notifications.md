# ADR 005: Admin bot notifications on registration changes

## Status

Accepted

## Context

Organizers need to know when users register or cancel without opening the Mini App. MVP PRD listed user-facing automated notifications as out of scope, but lightweight admin-only Telegram messages were requested explicitly.

## Decision

When a user registers or cancels via the API, send a Markdown message to every ID in `ADMIN_TELEGRAM_IDS`:

- Register: `@name будет на *event name* *date*` + participant count
- Cancel: `@name отменил(а) регистрацию на *event name* *date*` + participant count

Delivery failures are logged and do not block the registration API response.

## Consequences

- Admins get real-time visibility in the same bot they use for `/admin`
- No user-facing push/email (still out of scope)
- Requires `BOT_TOKEN` and `ADMIN_TELEGRAM_IDS` on the backend (already required for admin panel)

## Addendum (ADR-025, 2026-08-18)

On events with `requires_approval`, a **new application** (`pending`) is not «будет на». Send a DM with **«Принять» / «Отклонить»** instead (copy in ADR-025). User cancel of a pending row still uses cancel wording, without decision buttons. Open events keep this ADR unchanged. User DMs on accept/reject are specified in ADR-025 (exception to “no user-facing push” for the approval gate only).
