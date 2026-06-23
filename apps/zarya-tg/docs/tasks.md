# zarya — Task Backlog

## Status Legend

`[ ]` Not started · `[~]` In progress · `[x]` Done · `[-]` Blocked

---

## Phase 0 — Repository & Documentation

- [x] Initialize GitHub repository
- [x] Add README.md with project overview
- [x] Add .gitignore
- [x] Create project folder structure
- [x] Add AGENTS.md for AI agent context
- [x] Add .cursor/rules for Cursor AI
- [x] Add docs/prd.md (PRD v4.0)
- [x] Add docs/ux_ui_analysis.md
- [x] Add UI/UX mockups to docs/deliverables/
- [x] Add docs/tasks.md (this file)
- [x] Add docs/decisions/001-stack.md (stack decision record)

---

## Phase 1 — Backend Foundation

- [x] Initialize FastAPI project in `backend/`
- [x] Set up PostgreSQL schema (Users, Events, Registrations)
- [x] Configure Railway deployment (Dockerfile + railway.toml)
- [x] Implement Telegram bot skeleton with aiogram
- [x] Implement admin authentication (Telegram ID check)
- [x] Implement event CRUD API endpoints
- [x] Implement image upload handling (cover images)
- [x] Implement registration/cancellation endpoints
- [x] Implement .ics calendar file generation
- [x] Write basic API tests

---

## Phase 2 — Frontend (Telegram Mini App)

- [x] Initialize React + TypeScript project in `frontend/`
- [x] Integrate Telegram Web App SDK
- [x] Build home screen (event list with cover images)
- [x] Build event details screen (modal or new screen)
- [x] Build registration flow (register / cancel)
- [x] Build "My Registrations" screen
- [x] Implement navigation icon toggle (🎫 / 🏠)
- [x] Implement calendar export button (.ics download)
- [x] Apply zarya design system (dark theme, amber accent)
- [x] Connect frontend to backend API

---

## Phase 3 — Admin Interface

- [x] Implement `/admin` command in Telegram bot
- [x] Implement event creation flow (name, date, time, location, description, image)
- [x] Implement event editing flow
- [x] Implement event deletion with confirmation
- [x] Implement event list view with registration counts

---

## Phase 4 — Testing & Deployment

- [ ] End-to-end testing with real Telegram accounts
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Railway (static hosting)
- [ ] Configure Telegram bot webhook
- [ ] Invite initial 20 users and validate flows
- [ ] Fix bugs from user testing

---

## Iteration 2 — Future Backlog

- [ ] Access codes for zarya + circle events
- [ ] User profiles (name, avatar)
- [ ] Event categories and filters
- [ ] Automated notifications
- [ ] English localization
- [ ] Analytics dashboard
