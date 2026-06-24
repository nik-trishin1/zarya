# ADR-010: Event Share Deep Links

**Date:** 2026-06-23
**Status:** Accepted

## Context

Users need to share a specific event with friends in Telegram chats. Recipients should open the Mini App directly on that event's detail screen.

## Decision

Use Telegram Mini App direct links with the `startapp` query parameter:

```
https://t.me/{bot_username}?startapp=event_{event_id}&startApp=event_{event_id}&mode=fullscreen
```

`startApp` (camelCase) is duplicated for older iOS Telegram clients. `mode=fullscreen` opens the Mini App in full screen instead of a compact sheet.

If the bot has a **Direct Link** Mini App short name in BotFather, use:

```
https://t.me/{bot_username}/{short_name}?startapp=event_{event_id}&startApp=event_{event_id}&mode=fullscreen
```

Configured via optional `VITE_BOT_APP_SHORT_NAME` (frontend) / `BOT_APP_SHORT_NAME` (backend announcements).

On launch, the frontend reads `start_param` from `WebApp.initDataUnsafe` (or `tgWebAppStartParam` in the URL) and opens the event detail overlay for the matching ID.

A **«Поделиться»** button on the event detail screen generates this link and opens Telegram's native share dialog via `t.me/share/url` with separate `url` and `text` parameters. Passing the deep link in the `url` field (not only as plain text) is required so iOS treats it as a native Telegram link instead of opening Safari. Outside Telegram, the link is copied to the clipboard.

Bot username is configured via `VITE_BOT_USERNAME` (default: `zarya_friends_bot`, production bot **@zarya_friends_bot**).

Admin bot does not expose share links — sharing is user-facing only from the Mini App event card.

## Alternatives Considered

**`?start=event_42` (bot deep link).** Opens the bot chat first; requires an extra tap to launch the Mini App. Rejected for worse UX.

**URL hash routing (`/event/42`).** Not passed through Telegram's Mini App launcher; `startapp` is the supported mechanism.

## Consequences

- Past or deleted events may still open via direct link (`GET /events/{id}` returns any event).
- Past events show **«Событие прошло. Stay tuned!»** and a disabled register button; the API rejects new registrations with HTTP 410.
- Registered users who open a past event via link still see their registration status and calendar actions.
- `start_param` must match `event_{id}` with only digits after the underscore.
- Production frontend must set `VITE_BOT_USERNAME` on Railway if the bot handle changes (current production: `zarya_friends_bot`).
- On iOS, shared links that contain only plain-text URLs may open in Safari; always share via `t.me/share/url?url=...&text=...`.
- If iOS still opens a web page instead of the Mini App, set `VITE_BOT_APP_SHORT_NAME` to the short name from BotFather → Bot Settings → Mini Apps → Direct Links.
