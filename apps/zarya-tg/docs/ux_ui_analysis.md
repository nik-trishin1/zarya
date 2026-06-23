# UX/UI Analysis: Best Practices for zarya MVP

## 1. luma.com Analysis

luma.com is the primary UX benchmark for zarya. Key observations from a Product Manager and UX Designer perspective are as follows.

**What luma.com does well.** The home page surfaces popular events immediately without requiring navigation. Event cards include a cover image, creating visual appeal and enabling fast scanning. Information hierarchy is clear: date, title, location. A single tap on a card opens event details. The overall design is minimal and uncluttered.

**What zarya improves upon.** On luma.com, the full event discovery flow requires three extra taps before the user reaches the event list. zarya eliminates this by making the event list the home screen itself — the user opens the app and immediately sees all events.

## 2. @invites_tgbot Analysis

@invites_tgbot is the closest direct Telegram-native benchmark.

**What it does well.** The bot keeps the interface minimal and focused. Registration is a single action. Cover images are displayed at a medium size — not full-screen — which balances visual appeal with content density. The overall flow is fast and low-friction.

**What zarya improves upon.** zarya uses a Mini App (Web App) instead of a pure text bot, enabling a richer visual interface, card-based layouts, and native-feeling navigation that a text bot cannot provide.

## 3. Core UX Principles for zarya

**Shortest path to value.** The critical path from opening the app to completing a registration must be no more than two taps: open app → tap event card → tap "Зарегистрироваться". Every additional step is a potential drop-off point.

**Home screen = event list.** There is no intermediate menu or splash screen. The user lands directly on the chronological event list. This eliminates one tap compared to apps that require navigating to a separate "Events" section.

**Single navigation element.** With only two screens (event list and my registrations), a bottom tab bar wastes ~50px of vertical space. A single icon in the top-left corner serves as the toggle: 🎫 on the home screen navigates to "My Registrations"; 🏠 on the registrations screen returns home.

**Cover images in MVP.** Visual thumbnails make events feel real and scannable. The admin uploads a cover image when creating an event. A colored fallback block is shown when no image is provided.

## 4. Screen-by-Screen UX Notes

### Home Screen (Event List)

The screen opens directly to a chronological list of all upcoming events. Each event card displays: cover image (medium size, ~120px height), date and time, event title, location, and a registration status indicator (✅ if registered, empty if not). The entire card is tappable and opens the event details screen.

```
┌─────────────────────────────────────┐
│ [🎫]  zarya + friends 🌅            │  ← header + nav icon
├─────────────────────────────────────┤
│  [Cover Image]                      │
│  Fri, 28 Jun · 19:00                │
│  Вечеринка в доме                   │
│  Мой дом, Москва            [✅]    │
├─────────────────────────────────────┤
│  [Cover Image]                      │
│  Sat, 5 Jul · 15:00                 │
│  Кино-вечер                         │
│  Мой дом, Москва                    │
└─────────────────────────────────────┘
```

### Event Details Screen

Reached by tapping any event card. Displays: medium cover image at the top, event title, date/time/location, full description, and a primary action button. If the user is not registered, the button reads "Зарегистрироваться". If registered, the button is replaced by a green "Вы зарегистрированы ✅" chip, a secondary "Добавить в календарь" button, and a muted "Отменить регистрацию" link.

### My Registrations Screen

Accessed via the 🎫 icon. Shows only events the user has registered for, using the same card layout as the home screen. The 🏠 icon in the top-left returns to the home screen.

### Registration Success State

After a successful registration, a toast notification appears confirming the action and offering a one-tap "Добавить в календарь →" shortcut to download the `.ics` file.

## 5. Design System

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#0D0D0D` | App background |
| Card surface | `#1C1C1E` | Event cards |
| Accent | `#E8874A` | Primary buttons, highlights |
| Text primary | `#F5F0E8` | Headings, titles |
| Text secondary | `#888888` | Date, location |
| Success | `#4CAF50` | Registered status |
| Border radius | `16px` cards · `12px` buttons | Consistent rounding |

## 6. Benchmark Comparison

| Dimension | luma.com | @invites_tgbot | zarya (target) |
|-----------|----------|----------------|----------------|
| Platform | Web | Telegram bot | Telegram Mini App |
| Steps to registration | 4+ | 3 | 2 |
| Cover images | Yes | Yes (medium) | Yes (medium) |
| Navigation | Top nav + tabs | Text commands | Single icon toggle |
| Event list on home | Partial | No | Yes |
| Calendar export | Yes | No | Yes (.ics) |
