# zarya MVP - Product Requirements Document (PRD) v4.0

## 1. Executive Summary

zarya is a Telegram Mini App (Web App) community event management platform designed to help small groups (initially ~20 friends) organize, discover, and register for social gatherings. The MVP features a streamlined, mobile-first interface where users open the app and immediately see all upcoming events as beautiful cards with cover images. Registration is just two taps away: tap an event to see details, tap to register. The prototype will demonstrate core functionality: event discovery with visual appeal, registration, and calendar integration. Success is measured by: (1) all 20 initial users can register for at least one event within the first week, (2) the bot correctly manages event registration status, and (3) the admin can create and manage events without friction.

## 2. Problem Statement & Success Measures

**Core Problem:**
Small friend groups lack a centralized, low-friction way to organize recurring social events. Current solutions (WhatsApp groups, shared notes, email) create friction: scattered information, no unified RSVP tracking, and poor event discoverability. zarya solves this by providing a single, always-accessible interface (Telegram Mini App) with a streamlined UX that minimizes the path to registration. Events are discovered immediately upon opening the app, and registration requires just two taps.

**Success Measures (MVP Phase):**
1. **User Adoption:** ≥18 of 20 invited users open the app and complete at least one action (view event, register) within 48 hours of receiving the bot link.
2. **Registration Accuracy:** 100% of registrations are correctly recorded, with no data loss or duplicate entries across 50+ test registrations.
3. **Admin Usability:** Admin can create a new event with cover image and have it appear in the app for all users within 2 minutes.

## 3. Goals & Non-Goals

**In Scope (MVP):**
- Event creation and management (admin-only, via Telegram commands).
- Event browsing and discovery in chronological order (public tier only; zarya + friends).
- Event cover images (admin uploads during event creation).
- User registration and cancellation for events.
- Event details display (name, date, time, location, description, cover image, registration status).
- Calendar export functionality (.ics file) for registered events.
- Telegram Mini App (Web App) UI with Russian language.
- Bottom tab bar navigation (Events / My Registrations).
- Admin panel for event and user management (accessible via `/admin` command).
- Deployment to Railway for continuous availability.

**Out of Scope (MVP, moved to Iteration 2):**
- Access codes and circle-tier events (zarya + circle, zarya + core).
- User profile management and persistence (name, avatar, bio).
- Event categorization and filtering (Tech, Food & Drink, etc.).
- Geographical filtering and location-based discovery.
- Automated notifications (email/SMS/push).
- Photo galleries or post-event content.
- User-to-user messaging or social features.
- Participant list visibility (users cannot see who else is registered).
- Mobile app (Telegram Mini App only; no native iOS/Android app).
- Automated email invitations or calendar integrations beyond .ics export.
- Analytics dashboard or reporting.
- Localization beyond Russian (English support in Iteration 2+).

## 4. Target Personas & JTBD

**Persona 1: Event Organizer (Creator)**
- Age: 25–40, tech-savvy entrepreneur or community leader.
- Goal: Centralize event management without learning new tools; manage registrations easily.
- JTBD: Create events with cover images, manage registrations, view attendance count, edit/delete events.

**Persona 2: Event Participant (Friend)**
- Age: 20–40, active in social circles, uses Telegram daily.
- Goal: Discover upcoming events instantly, register easily, add events to personal calendar.
- JTBD: Browse events, register/unregister, receive event details, export to calendar.

## 5. User Stories (Must-Have Only)

### Must-Have Stories

**US-1: User Onboarding**
- As a new user, I want to open the Telegram Mini App and immediately see upcoming events so that I can discover what's happening without extra steps.
- Acceptance Criteria:
  - User receives bot link (e.g., `t.me/zarya_friends_bot?startapp=event_5&startApp=event_5`) and taps it.
  - Telegram opens the Mini App (Web App).
  - App displays the home screen with all upcoming events in chronological order.
  - No welcome screen or extra steps; events are the primary content.
  - User's Telegram ID is automatically captured (no manual registration needed).
  - Header shows: [🎫] zarya + friends 🌅 (navigation icon in top-left corner)
- Priority: MUST

**US-2: Browse Events (Chronological Order with Cover Images)**
- As a participant, I want to see all upcoming events as visually appealing cards with cover images so that I can quickly discover and identify events.
- Acceptance Criteria:
  - Home screen displays a list of all upcoming events sorted by date (earliest first).
  - No date range limit (all future events are shown).
  - Each event card shows:
    - Cover image (80x80px or larger, depending on layout)
    - Date and time (e.g., "Пт, 28 июня, 19:00")
    - Event name
    - Location
    - Registration status indicator (✅ if registered, empty if not)
  - Event cards are visually clean and minimal, inspired by luma.com design.
  - Entire event card is clickable (not just a button).
  - If no events exist, app shows: "Нет предстоящих событий" (No upcoming events).
- Priority: MUST

**US-3: View Event Details**
- As a participant, I want to tap an event card and see full details so that I can decide whether to attend.
- Acceptance Criteria:
  - User taps an event card from the home screen.
  - App displays a modal or new screen with:
    - Medium-sized cover image at the top (similar to @invites_tgbot style; ~200px height)
    - Event name
    - Date, time, location
    - Full description
    - Current registration count (e.g., "Зарегистрировано: 5 человек")
    - Action button: "Зарегистрироваться" (if not registered) or "Отменить регистрацию" (if registered)
    - "Добавить в календарь" button (if registered)
    - Navigation icon in top-left corner (🏠 to return to home)
  - Participant list is NOT visible to users (hidden for privacy).
- Priority: MUST

**US-4: Register for Event**
- As a participant, I want to register for an event with one tap so that I can confirm my attendance.
- Acceptance Criteria:
  - User views event details and taps "Зарегистрироваться" (Register).
  - App confirms: "Вы зарегистрированы на [Event Name] на [Date]" (You're registered for [Event Name] on [Date]).
  - Button changes to "Отменить регистрацию" (Cancel Registration).
  - Registration count increments by 1.
  - Event card on home screen now shows ✅ indicator.
  - User's registration status is stored in the database.
- Priority: MUST

**US-5: Cancel Registration**
- As a participant, I want to unregister from an event if my plans change so that my spot can go to someone else.
- Acceptance Criteria:
  - User views event details and taps "Отменить регистрацию" (Cancel Registration).
  - App confirms: "Вы отменили регистрацию на [Event Name]" (You've cancelled registration for [Event Name]).
  - Button changes to "Зарегистрироваться" (Register).
  - Registration count decrements by 1.
  - Event card on home screen no longer shows ✅ indicator.
  - User's registration is removed from the database.
- Priority: MUST

**US-6: View My Registrations**
- As a participant, I want to tap the navigation icon and see all events I'm registered for so that I don't forget upcoming plans.
- Acceptance Criteria:
  - User taps the 🎫 icon in the top-left corner of the header (on the home screen).
  - App displays a list of upcoming events the user is registered for, sorted by date (past events are hidden, not deleted; see ADR-018).
  - Ticket counter (🎫 badge) counts only upcoming registrations.
  - Each event card shows the same information as on the home screen (cover image, date, time, name, location, ✅ indicator).
  - Header now shows: [🏠] zarya + friends 🌅 (icon changes to 🏠 to return home).
  - User can tap an event to see full details or cancel registration.
  - If no upcoming registrations exist, app shows: "Вы не зарегистрированы ни на какие события" (You're not registered for any events).
- Priority: MUST

**US-7: Export Event to Calendar**
- As a participant, I want to add a registered event to my personal calendar so that I don't forget about it.
- Acceptance Criteria:
  - After successfully registering for an event, the event details screen displays a button: "Добавить в календарь" (Add to Calendar).
  - User taps the button.
  - App generates a .ics (iCalendar) file with event details: name, date, time, location, description.
  - User can download or open the .ics file in their calendar app (Google Calendar, Apple Calendar, Outlook, etc.).
  - The .ics file includes: SUMMARY (event name), DTSTART (date/time), LOCATION, DESCRIPTION.
- Priority: MUST

**US-8: Admin - Create Event with Cover Image**
- As the event organizer (admin), I want to create new events with details and upload a cover image so that events are visually appealing and easy to identify.
- Acceptance Criteria:
  - Admin sends `/admin` command in Telegram chat with the bot.
  - Bot authenticates admin (Telegram ID check against hardcoded list).
  - Bot displays an admin menu with options: "Создать событие" (Create Event), "Управлять событиями" (Manage Events).
  - Admin selects "Создать событие" and is prompted for: название (name), дата (date), время (time), место (location), описание (description).
  - Admin is prompted to upload a cover image (JPEG, PNG, max 5MB).
  - If no image is provided, a default placeholder is used.
  - Admin confirms the event details.
  - Bot confirms: "Событие создано: [Event Name] на [Date]" (Event created: [Event Name] on [Date]).
  - Event is stored in the database with cover image and immediately visible to all users in the app.
- Priority: MUST

**US-9: Admin - Edit Event**
- As the event organizer, I want to edit event details after creation so that I can fix mistakes or update information.
- Acceptance Criteria:
  - Admin selects "Управлять событиями" (Manage Events) from admin menu.
  - Bot displays a list of upcoming events only (past events stay in the database but are hidden; see ADR-018).
  - Admin selects an event and chooses "Редактировать" (Edit).
  - Admin is prompted to update: название, дата, время, место, описание, cover image (optional).
  - Admin confirms the changes.
  - Bot confirms: "Событие обновлено: [Event Name]" (Event updated: [Event Name]).
  - Changes are immediately reflected in the app for all users.
- Priority: MUST

**US-10: Admin - Delete Event**
- As the event organizer, I want to delete an event if it's cancelled so that users don't see outdated information.
- Acceptance Criteria:
  - Admin selects "Управлять событиями" (Manage Events) from admin menu.
  - Admin selects an event and chooses "Удалить" (Delete).
  - Bot asks for confirmation: "Вы уверены? Это действие нельзя отменить." (Are you sure? This action cannot be undone.)
  - Admin confirms.
  - Bot confirms: "Событие удалено: [Event Name]" (Event deleted: [Event Name]).
  - Event is removed from the database and no longer visible in the app.
- Priority: MUST

**US-11: Admin - View Event List**
- As the event organizer, I want to see upcoming events and their registration details so that I can manage attendance.
- Acceptance Criteria:
  - Admin selects "Управлять событиями" (Manage Events) from admin menu.
  - Bot displays a list of upcoming events with: name, date, registration count (past events hidden, not deleted; see ADR-018).
  - If there are no upcoming events, bot shows: "Нет предстоящих событий."
  - Admin can select an event to see: full details, registration count, and options to edit or delete.
  - Bot shows: "Событие: [Name] | Дата: [Date] | Зарегистрировано: [Count] человек" (Event: [Name] | Date: [Date] | Registered: [Count] people).
- Priority: MUST

## 6. Key Flows & UX Notes

### Application Structure

The app uses a minimalist header with a navigation icon in the top-left corner, keeping the interface clean and mobile-friendly. The home screen is the primary interface, displaying all upcoming events as visually appealing cards with cover images. Users can tap any card to see full details and register with a single additional tap.

```
┌─────────────────────────────────────┐
│ [🎫]  zarya + friends 🌅            │  ← Header with nav icon
├─────────────────────────────────────┤
│                                     │
│  [Event Card 1 with cover image]    │
│  [Event Card 2 with cover image]    │
│  [Event Card 3 with cover image]    │
│  ...                                │
│                                     │
└─────────────────────────────────────┘
```

**Navigation Icon:** The icon in the top-left corner toggles between:
- 🎫 (My Registrations) when on the home screen
- 🏠 (Home) when on the My Registrations screen
No text labels; icon-only for minimal space usage.

### Main User Flow (Participant)

The user experience is designed to minimize friction. When a user opens the app, they immediately see all upcoming events as beautiful cards with cover images. Registration is just two taps away: tap an event to see details, tap to register.

1. **Open App:** User opens the Telegram Mini App. Home screen displays all upcoming events in chronological order, each as a card with cover image, date, time, name, and location.

2. **Browse Events:** User scrolls through the event list. Each card is visually distinct thanks to the cover image. Registration status (✅) is visible on cards where the user is already registered.

3. **View Details:** User taps an event card. A modal or new screen opens showing the full event details: large cover image, name, date, time, location, description, registration count, and action button.

4. **Register:** User taps "Зарегистрироваться" (Register). App confirms the registration and offers to add the event to their calendar.

5. **Add to Calendar (Optional):** User taps "Добавить в календарь" (Add to Calendar). App generates and downloads a .ics file.

6. **Return to Home:** User taps "Назад" (Back) or swipes down to close the modal. Returns to the home screen where the event card now shows ✅ indicator.

### My Registrations Screen

1. **Tap Navigation Icon:** User taps the 🎫 icon in the top-left corner of the header.

2. **View Registrations:** App displays a list of upcoming events the user is registered for, sorted by date (past events hidden; ADR-018). Same card design as home screen. Header icon changes to 🏠.

3. **Return Home:** User taps the 🏠 icon in the top-left corner to return to the home screen.

4. **Manage:** User can tap any event to see details or cancel registration.

### Admin Flow (Event Organizer)

The admin interface is accessed via Telegram commands and remains separate from the user-facing Mini App. This keeps the user experience clean while providing the admin with all necessary management tools.

1. **Authenticate:** Admin sends `/admin` command in Telegram chat. Bot verifies Telegram ID against hardcoded admin list.

2. **Create Event:** Admin selects "Создать событие" (Create Event), fills in details via bot prompts (name, date, time, location, description), and uploads a cover image. Event is immediately live in the app.

3. **Manage Events:** Admin selects "Управлять событиями" (Manage Events) to view upcoming events and edit/delete as needed (past events hidden; ADR-018).

4. **Edit Event:** Admin selects an event, chooses "Редактировать" (Edit), updates details and cover image, and confirms. Changes appear immediately in the app.

5. **Delete Event:** Admin selects an event, chooses "Удалить" (Delete), confirms, and the event is removed.

### UX Notes

**Design Philosophy:** The design is inspired by luma.com's minimalist approach with a focus on visual appeal through cover images. The interface is mobile-first, with a bottom tab bar for easy navigation. Every interaction is designed to minimize friction and get users to registration as quickly as possible.

**Telegram Mini App:** All user interactions happen in a Web App embedded in Telegram (not in the chat interface). This provides a modern, app-like experience with better UX than a text-only bot.

**Language:** All text is in Russian (Русский язык). Localization to English is deferred to Iteration 2.

**Bot Personality:** Messages use the zarya brand voice: warm, inviting, minimalist. Emoji use is subtle (🌅 for zarya, ✅ for confirmation, 📅 for calendar).

**Navigation:** Single navigation icon in the top-left corner of the header. Icon toggles between 🎫 (My Registrations) on home screen and 🏠 (Home) on My Registrations screen. Icon-only design maximizes screen space for event content.

**Event Cards:** Each card displays cover image, date/time, event name, location, and registration status. Entire card is clickable. Cards are consistent across home screen and "My Registrations" tab.

**Admin Interface:** Admin interactions happen via Telegram chat commands (`/admin`, etc.). This keeps admin functions separate from the user-facing Mini App.

**Confirmation Messages:** Every action (register, cancel, create event) is confirmed with a clear, brief message in Russian.

**Error Handling:** Invalid inputs or system errors show user-friendly messages with suggested next steps (all in Russian).

**No Participant List:** Users cannot see who else is registered for an event (privacy by design).

**Calendar Export:** The .ics file is generated on-the-fly and can be downloaded or opened directly in the user's calendar app. The file includes all relevant event details.

## 7. Feature List & Mock/Manual Flags

| Feature | Status | Notes |
|---------|--------|-------|
| Telegram Mini App (Web App) | Real | React or Vue.js frontend; embedded in Telegram. |
| Home Screen (Events List) | Real | Chronological order; all future events; cover images. |
| Event Cards with Cover Images | Real | 80x80px on list; ~200px in details (medium size). |
| Navigation Icon | Real | 🎫 on home screen; 🏠 on My Registrations screen; top-left corner. |
| Event Details Modal/Screen | Real | Full event info; medium-sized cover image (~200px); registration button. |
| Event Registration | Real | Inserts record into registrations table; updates count. |
| Event Cancellation | Real | Deletes registration record; updates count. |
| My Registrations Tab | Real | Lists registered events; same card design. |
| Calendar Export (.ics) | Real | Generates .ics file on-the-fly; includes event details. |
| Admin Authentication | Real | Checks Telegram ID against hardcoded admin list. |
| Event Creation with Cover Image | Real | Admin uploads image; stored in S3 or Railway. |
| Event Editing | Real | Admin updates details and cover image. |
| Event Deletion | Real | Admin deletes event; removed from database. |
| Event Management (Admin) | Real | Admin views upcoming events with registration counts (past hidden; ADR-018). |
| Event Categorization | Not Implemented | Deferred to Iteration 2. |
| Access Codes (Circle Tier) | Not Implemented | Deferred to Iteration 2. |
| User Profiles | Not Implemented | Deferred to Iteration 2. |
| Notifications | Manual | Admin manually reminds users (outside app). |
| Photo Uploads (Post-Event) | Not Implemented | Future feature; out of MVP scope. |
| User-to-User Messaging | Not Implemented | Out of MVP scope. |

## 8. Data Model & External Integrations

### Entity-Relationship Diagram (Simplified)

```
Users
├── user_id (PK)
├── telegram_id (unique)
├── username (nullable)
├── first_name (nullable)
└── created_at

Events
├── event_id (PK)
├── name
├── description
├── date
├── time
├── location
├── cover_image_url (nullable)
├── tier (friends only in MVP)
├── created_at
├── updated_at
└── created_by_admin_id (FK: Users)

Registrations
├── registration_id (PK)
├── user_id (FK: Users)
├── event_id (FK: Events)
├── registered_at
└── status (active, cancelled)
```

### External Integrations

**Telegram Bot API:** Used for admin interface and bot commands.
**Telegram Mini App (Web App API):** Used for user-facing app; communicates with bot backend via `window.Telegram.WebApp`.
**S3 or Railway File Storage:** Used for storing event cover images.
**iCalendar (.ics) Standard:** Used for calendar export; no external API required (generated locally).

## 9. Technical Stack Recommendation

### Recommended Stack (Fastest Path, MVP)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Bot Framework | `aiogram` (Python 3.11) | Async, well-documented, active community. |
| Frontend (Mini App) | React 18 + TypeScript | Fast development, component reusability, Telegram Web App SDK. |
| Backend | FastAPI (Python) | Async, lightweight, easy to integrate with aiogram. |
| Database | PostgreSQL | Scales better than SQLite; Railway provides managed PostgreSQL. |
| File Storage | Railway Volumes or S3 | For storing event cover images. |
| Hosting | Railway.com (free tier or paid) | Simple deployment, auto-scaling, integrated PostgreSQL. |
| Calendar Export | ics library (Python) | Lightweight, no external dependencies. |
| Environment | Python 3.11 + Node.js 18+ | Pre-installed in most environments. |
| Deployment | Docker (Railway native) | Simplifies deployment and scaling. |

**Pros:** Modern stack, scalable, Railway handles DevOps, fast iteration, no external APIs for calendar export, integrated file storage.
**Cons:** Slightly more complex than SQLite + simple bot; requires Docker knowledge.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Platform                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐        ┌──────────────────────┐   │
│  │   Telegram Bot       │        │   Telegram Mini App  │   │
│  │  (Admin Interface)   │        │   (User Interface)   │   │
│  │  - /admin command    │        │  - React + TypeScript│   │
│  │  - Event CRUD        │        │  - Event browsing    │   │
│  │  - Image upload      │        │  - Registration      │   │
│  │  - User management   │        │  - Calendar export   │   │
│  └──────────┬───────────┘        └──────────┬───────────┘   │
│             │                               │                │
│             └───────────────┬───────────────┘                │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   FastAPI       │                       │
│                    │   Backend       │                       │
│                    │ - Event API     │                       │
│                    │ - User API      │                       │
│                    │ - Reg API       │                       │
│                    │ - Calendar API  │                       │
│                    │ - Image upload  │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│          ┌──────────────────┼──────────────────┐             │
│          │                  │                  │             │
│    ┌─────▼─────┐    ┌──────▼──────┐    ┌─────▼─────┐       │
│    │PostgreSQL │    │   Railway   │    │    S3 or  │       │
│    │    DB     │    │  Volumes    │    │  Railway  │       │
│    │(Railway)  │    │ (File Store)│    │  Storage  │       │
│    └───────────┘    └─────────────┘    └───────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 10. Privacy, Security & Compliance Considerations

**Data Handling:**
- User Telegram IDs and usernames are stored; treat as PII.
- No passwords required (Telegram OAuth implicit).
- No payment data stored (out of MVP scope).
- Participant lists are not stored or displayed (privacy by design).
- Event cover images are stored securely in Railway Volumes or S3.

**Security Measures (MVP):**
- Admin authentication via hardcoded Telegram ID list (sufficient for small team).
- All data transmitted over HTTPS (Railway provides SSL by default).
- PostgreSQL database is managed by Railway (automatic backups, encryption at rest).
- Bot token is stored in environment variables (never hardcoded).
- File uploads are validated (JPEG/PNG, max 5MB).

**Compliance:**
- **GDPR (if EU users):** Provide a `/delete_account` command to remove user data on request.
- **Telegram Terms of Service:** Bot must not spam, scrape, or abuse the platform. zarya complies (one-to-one messages only, no unsolicited broadcasts).
- **Russia/CIS Regulations:** No specific compliance required for MVP (community-only, non-commercial).

**Recommendations:**
- Add a privacy policy link in bot description.
- Implement `/delete_account` command for GDPR compliance.
- Log all admin actions (event creation, deletion, image uploads) for audit trail.
- Use environment variables for all secrets (bot token, admin IDs, database URL).

## 11. Instrumentation & Feedback Loop

### Events to Track (Telemetry)

| Event | Trigger | Metric | Rationale |
|-------|---------|--------|-----------|
| `user_opened_app` | User opens Mini App | Daily active users | Engagement metric. |
| `event_list_viewed` | User views home screen | Event discovery rate | Engagement metric. |
| `event_details_viewed` | User taps an event card | Event interest | Engagement metric. |
| `event_registered` | User taps "Зарегистрироваться" | Registration rate | Core action metric. |
| `event_cancelled` | User taps "Отменить регистрацию" | Cancellation rate | Churn metric. |
| `calendar_exported` | User taps "Добавить в календарь" | Calendar adoption | Feature usage. |
| `admin_event_created` | Admin creates event | Event creation rate | Content generation. |
| `admin_event_edited` | Admin edits event | Event management activity | Admin engagement. |
| `admin_event_deleted` | Admin deletes event | Event lifecycle | Admin engagement. |
| `admin_image_uploaded` | Admin uploads cover image | Image adoption | Feature usage. |

### Qualitative Feedback

- **Manual Survey:** Founder asks users directly (outside app) about their experience and suggestions.
- **Usability Testing:** Invite 3–5 users to test the app and observe friction points (e.g., unclear buttons, confusing flows).

### Success Metrics Capture

- **Adoption:** Count app opens; target ≥18 of 20 users within 48 hours.
- **Engagement:** Count event views and registrations; target ≥50% of users registering for at least one event in week 1.
- **Calendar Adoption:** Count calendar exports; target ≥30% of registrations result in calendar export.
- **Image Adoption:** Count events with cover images; target 100% of new events have images.
- **Data Integrity:** Manually verify registrations against database; target 100% accuracy.

## 12. Timeline & Resourcing (Prototype Phase)

### Week-by-Week Plan (6 weeks, MVP-focused)

| Week | Deliverable | Owner Role | Notes |
|------|-------------|-----------|-------|
| 1 | Project setup, DB schema, bot skeleton, Mini App scaffold | Tech Lead | FastAPI + React setup; Telegram Bot API integration; file storage setup. |
| 2 | Mini App: home screen (event list with cover images), event details UI, navigation icon | Frontend Dev | React components; API integration; image display; luma.com-inspired design; toggle navigation. |
| 3 | Backend: event API, registration logic, image upload handling | Backend Dev | FastAPI endpoints; database queries; file storage integration. |
| 4 | Mini App: registration UI, my registrations tab, calendar export, bottom tab bar | Frontend Dev | Button interactions; state management; .ics file generation; tab navigation. |
| 5 | Admin interface: event CRUD with image upload via bot | Backend Dev | Bot commands; admin authentication; file upload handling. |
| 6 | Testing, bug fixes, deployment to Railway | QA / Tech Lead | End-to-end testing; Railway setup; image storage verification. |

**Resourcing:** 1 Tech Lead (part-time, weeks 1–6) + 1 Frontend Dev (full-time, weeks 2–4) + 1 Backend Dev (full-time, weeks 3–5) + 1 QA (part-time, weeks 5–6).

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| **Telegram Mini App API limitations** | Medium | Medium | Research Telegram Web App SDK early; test with sample Mini App. |
| **Image upload/storage issues** | Medium | Medium | Test file upload flow early; use Railway Volumes as primary storage. |
| **PostgreSQL connection issues** | Low | High | Use connection pooling; implement retry logic with exponential backoff. |
| **Admin authentication bypass** | Low | High | Use secure random token generation; store hashed admin IDs. |
| **User confusion (unclear UI)** | High | Low | Conduct usability testing with 3–5 users; iterate on button labels and flows. |

## 14. Open Questions & Assumptions

**Assumptions (Confirmed):**
1. All 20 initial users have active Telegram accounts and check messages daily. ✅
2. Events are created by a single admin (no multi-admin support in MVP). ✅
3. Participant lists are NOT visible to users (privacy by design). ✅
4. Events have unlimited capacity (no waitlist logic in MVP). ✅
5. No date range limit on event browsing; all future events are shown. ✅
6. Calendar export is via .ics file (standard, no external API). ✅
7. Event cover images are uploaded by admin during event creation. ✅
8. Access codes and circle-tier events are deferred to Iteration 2. ✅
9. User profiles are not needed in MVP; only Telegram ID and username. ✅
10. Interface is in Russian only; English localization in Iteration 2+. ✅
11. Deployment is to Railway.com (free or paid tier). ✅
12. Bottom tab bar is used for navigation (not hamburger menu). ✅
13. Home screen displays events immediately (no welcome screen). ✅

**Decisions Made:**
1. All events are shown in chronological order without date range limit. ✅
2. Calendar export uses .ics file format (compatible with all major calendar apps). ✅
3. Design is inspired by luma.com (clean, minimal) with cover images. ✅
4. Telegram Mini App (Web App) is used instead of text-only bot. ✅
5. Event cover images are included in MVP (not deferred). ✅
6. Bottom tab bar navigation minimizes friction to registration. ✅
7. Home screen is the primary interface (events visible immediately). ✅

## 15. Appendix

### Glossary

- **zarya + friends / public audience:** Events with no group (`audience_group_id` null); all bot users can see and register (ADR-020).
- **Access group (e.g. Core):** Named membership group; group events are visible only to members (admins bypass). Access codes (later) redeem into the same memberships.
- **zarya + circle / access codes:** Deferred (T-201); will grant membership in an access group, not a separate tier ACL.
- **Telegram Mini App (Web App):** A web-based interface embedded in Telegram; provides a modern, app-like UX.
- **Admin:** The event organizer (creator) who can create, edit, and delete events.
- **Participant:** A user registered for an event.
- **.ics File:** iCalendar format file; standard for calendar events; compatible with Google Calendar, Apple Calendar, Outlook, etc.
- **Cover Image:** Visual image displayed on event cards; helps identify and distinguish events.
- **Navigation Icon:** Single icon in the top-left corner of the header that toggles between 🎫 (My Registrations) and 🏠 (Home). Icon-only design minimizes space usage.

### Related Links

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Telegram Web App Documentation](https://core.telegram.org/bots/webapps)
- [aiogram Documentation](https://docs.aiogram.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Railway.com Documentation](https://docs.railway.app/)
- [React Documentation](https://react.dev/)
- [iCalendar (RFC 5545) Standard](https://tools.ietf.org/html/rfc5545)

### Research & Inspiration

- **luma.com:** Clean, minimal design for event cards; chronological sorting; user-friendly UX; cover images for visual appeal.
- **@invites_tgbot:** Simple, focused functionality; Telegram-native; minimal friction.
- **Tomorrowland Naming Philosophy:** Multi-tier event system with distinct atmospheres and access levels.
- **Surf Coffee Branding:** Modular naming convention (Surf x Location) applied to zarya (zarya + tier).
- **Mobile-First Design:** Bottom tab bar navigation; minimal friction; immediate value on app open.

---

**Document Version:** 4.0
**Last Updated:** 2026-06-23
**Status:** Ready for Development
**Deployment Platform:** Railway.com
**Frontend:** Telegram Mini App (React)
**Backend:** FastAPI + PostgreSQL
**Key Features:** Event browsing (chronological, with cover images), registration, calendar export (.ics), navigation icon
**UX Focus:** Minimal friction; registration in 2 taps; events visible immediately on app open; maximized screen space
