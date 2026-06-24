# ADR 009: Log and record users who blocked the bot

## Status

Accepted

## Context

When sending participant broadcasts, some messages fail because the user blocked the bot. Admins need visibility; the system should remember blocked contacts.

## Decision

- Detect `TelegramForbiddenError` with "bot was blocked by the user"
- Log at WARNING with `user_id`, `telegram_id`, `username`, `first_name`
- Store `users.bot_blocked_at` timestamp on first detected block
- Clear `bot_blocked_at` when a later message delivers successfully (user unblocked)
- Centralize delivery in `deliver_bot_message` used by broadcasts and admin notifications

## Consequences

- Railway deploy logs show who blocked the bot
- Database flag enables future filtering (e.g. skip blocked users in broadcasts)
- Admin broadcast summary reports blocked count separately from other failures
