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

## Iteration 2

> Scope finalised 2026-06-24. Items ordered by priority.

### Already shipped (confirmed during planning)

- [x] Event capacity limit (`max_participants` + `is_full` flag) — ADR-012
- [x] New event announcement broadcast to all users — ADR-011
- [x] Admin broadcast to all bot users from `/admin` — ADR-017
- [x] 24-hour reminder to registered participants — ADR-013
- [x] Shareable deep-link per event — ADR-010

### Backlog

- [ ] **Access codes for zarya + circle events** — unique personal codes granting access to hidden-tier events; admin generates and shares manually; no expiry by default but codes can be revoked. See ADR-015 (to be written).
- [ ] **Propose your own event** — any registered user can submit an event proposal (name, date, description); creates a `draft` event visible only to admin; admin approves → published with announcement, or rejects → draft deleted. See ADR-016 (to be written).
- [ ] **Past events status** — events past their date/time are visually marked "Завершено" with grey overlay; hidden from main list after 48h; accessible via future Archive section.
- [ ] **Event categories and filters** — categories: 🎉 Развлечения, ✈️ Путешествия, 📚 Образование, ☕ Встречи; filter chips in header; relevant when event count exceeds ~15.
- [ ] **English localization** — i18n layer (react-i18next on frontend, locale param on backend); Russian remains default.
- [ ] **Analytics dashboard** — admin-only view: total registrations per event, active users, monthly event count.

---

## Iteration 3

> Detailed requirements in `docs/decisions/014-event-ownership-and-inline-editing.md`.

- [ ] **Event ownership & in-app admin editing** — introduce `proposed_by_user_id` and `status` fields on Event; permission matrix (admin full access, initiator can edit own event and cancel it); in-app edit sheet (pencil icon on event details, visible when `can_edit: true`); cancellation triggers broadcast to registrants and DM to admin; bot FSM flow remains as supplementary interface.
- [ ] **Event duplication** — admin can copy an existing event as a template; all fields pre-filled except date/time.
- [ ] **Invite system** — unique invite link per user; admin sees who invited whom.
- [ ] **Web version** — public-facing zarya.org landing with upcoming events (read-only, no registration).
