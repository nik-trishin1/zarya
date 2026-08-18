# ADR 006: Admin participant list in bot

## Status

Accepted

## Context

MVP hides participant lists from regular users, but organizers need to see who registered. The admin bot already manages events; a participant list fits there without exposing data in the Mini App.

## Decision

Add «Участники» to the event management keyboard. Show a numbered list:

`1. Имя @username` (username omitted if unavailable)

## Consequences

- Admins can audit registrations without SQL or the Mini App
- User-facing participant list remains out of scope

## Addendum (ADR-025, 2026-08-18)

For `requires_approval` events, show a **Заявки** block **above** confirmed (active, seat-expanded) and maybe lines. Each pending line: `N. Имя @username — на рассмотрении` plus **Принять** / **Отклонить**. `Всего` footer remains **active seats only**. Maybe formatting (ADR-022) unchanged.
