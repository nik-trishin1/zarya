# ADR-017: Admin broadcast to all bot users

**Date:** 2026-07-10
**Status:** Accepted

## Context

Admins sometimes need to send a free-form message to the whole community, not only to registrants of one event. Event creation already supports optional announcement to all users in the `users` table (ADR-011). Participant broadcast (ADR-007) covers per-event registrants only.

Bulk delivery infrastructure exists: `deliver_bot_messages_to_users`, `bot_blocked_at` tracking (ADR-009).

## Decision

Add **📢 Написать всем** to the `/admin` main menu:

1. Admin enters message text
2. Bot shows preview with total user count
3. Admin confirms → message is sent to every row in `users`

Message body is the admin's text as-is (no event header). Delivery stats (sent / blocked / failed) match participant broadcast and new-event announcement.

Recipients are all users who have ever `/start`ed the bot or opened the Mini App.

## Alternatives Considered

**Reuse event announcement template.** Rejected — this flow is for arbitrary admin text, not a new event card.

**Broadcast from event menu.** Rejected — scope is all bot users, not event registrants.

## Consequences

- Same fan-out limits as ADR-011 (~20 users for MVP is fine).
- Users who blocked the bot are counted in `blocked`.
- Manual flow only; no scheduling or segmentation.
