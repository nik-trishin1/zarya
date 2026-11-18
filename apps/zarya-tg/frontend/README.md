# zarya-tg frontend

React 18 + TypeScript Telegram Mini App (Vite). Local: `npm install && npm run dev` (see app root `scripts/dev-local.sh`).

## Module map

| Path | Role |
|------|------|
| `src/main.tsx` | Vite entry; mounts `App` |
| `src/App.tsx` | Shell: header, screen switch, selected-event overlay |
| `src/routes.tsx` | Home / registrations screen bodies + empty states |
| `src/hooks/useEventsCache.ts` | Screen data fetch, per-screen cache, registration count |
| `src/hooks/useTelegram.ts` | Telegram WebApp ready/theme/safe-area |
| `src/api/client.ts` | REST client + `Event` types |
| `src/components/Header.tsx` | Top bar + 🎫/🏠 nav pill |
| `src/components/EventCard.tsx` | List row (home / my / archive) |
| `src/components/PosterSlider.tsx` | Featured home posters |
| `src/components/EventDetails.tsx` | Event overlay orchestrator (fetch + handlers) |
| `src/components/EventDetailsHeader.tsx` | Title, fact rows, description |
| `src/components/EventDetailsRegistration.tsx` | RSVP circles + +1 chip |
| `src/components/EventDetailsActions.tsx` | Cancel / share / calendar |
| `src/components/CoverImage.tsx` | Cover / placeholder image |
| `src/components/LinkifiedText.tsx` | Description linkify |
| `src/components/icons.tsx` | Shared SVG icons |
| `src/utils/deepLink.ts` | Start param + share links |
| `src/utils/format.ts` | Dates, seats, day groups |
| `src/utils/telegram.ts` | Init data, haptics, share sheet |
| `src/utils/calendar.ts` | `.ics` / prefilled calendar |
| `src/utils/theme.ts` | Theme CSS variables |
| `src/utils/linkify.ts` | URL detection for descriptions |

## Scripts

- `npm run lint` — ESLint
- `npm run build` — `tsc -b` + Vite production build
