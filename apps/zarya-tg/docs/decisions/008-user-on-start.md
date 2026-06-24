# ADR 008: Record users on bot /start

## Status

Accepted

## Context

Users were only persisted when opening the Mini App (API auth). Organizers may want to reach everyone who activated the bot, not only those who opened the app.

## Decision

Call `get_or_create_user` on `/start` and `/myid` bot commands, using the same `users` table and upsert logic as the Mini App.

## Consequences

- `/start` creates or updates `telegram_id`, `username`, `first_name`
- Enables future broadcasts to all known bot contacts
- Does not grant Mini App access or registration by itself
