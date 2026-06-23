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
- [ ] Add docs/decisions/001-stack.md (stack decision record)

---

## Phase 1 — Backend Foundation

- [ ] Initialize FastAPI project in `backend/`
- [ ] Set up PostgreSQL schema (Users, Events, Registrations)
- [ ] Configure Railway deployment (Dockerfile + railway.toml)
- [ ] Implement Telegram bot skeleton with aiogram
- [ ] Implement admin authentication (Telegram ID check)
- [ ] Implement event CRUD API endpoints
- [ ] Implement image upload handling (cover images)
- [ ] Implement registration/cancellation endpoints
- [ ] Implement .ics calendar file generation
- [ ] Write basic API tests

---

## Phase 2 — Frontend (Telegram Mini App)

- [ ] Initialize React + TypeScript project in `frontend/`
- [ ] Integrate Telegram Web App SDK
- [ ] Build home screen (event list with cover images)
- [ ] Build event details screen (modal or new screen)
- [ ] Build registration flow (register / cancel)
- [ ] Build "My Registrations" screen
- [ ] Implement navigation icon toggle (🎫 / 🏠)
- [ ] Implement calendar export button (.ics download)
- [ ] Apply zarya design system (dark theme, amber accent)
- [ ] Connect frontend to backend API

---

## Phase 3 — Admin Interface

- [ ] Implement `/admin` command in Telegram bot
- [ ] Implement event creation flow (name, date, time, location, description, image)
- [ ] Implement event editing flow
- [ ] Implement event deletion with confirmation
- [ ] Implement event list view with registration counts

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
