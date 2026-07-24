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

- [x] CI on PRs (pytest + frontend lint/build + Railway log scan) — see `process/ai-factory/CI.md`, ticket T-FACTORY-001
- [ ] Configure GitHub secrets/vars for Railway log scan (`RAILWAY_TOKEN`, `RAILWAY_SERVICE_NAMES`, …)
- [ ] End-to-end testing with real Telegram accounts
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Railway (static hosting)
- [ ] Configure Telegram bot webhook
- [ ] Invite initial 20 users and validate flows
- [ ] Fix bugs from user testing

---

## AI-Factory process

- [x] Portable process pack under `process/` — T-FACTORY-002 / S-FACTORY-001
- [x] Human-summary requirement on specs and tickets
- [x] Review gate + orchestrator docs
- [ ] Operator: create Cursor Automation `factory-implement` (see `process/ai-factory/ORCHESTRATOR.md`)

---

## Iteration 2

> Scope finalised 2026-06-24. Items ordered by priority.  
> Detailed tickets with Human summaries: [`docs/tickets/`](tickets/).

### Already shipped (confirmed during planning)

- [x] Event capacity limit (`max_participants` + `is_full` flag) — ADR-012
- [x] New event announcement broadcast to all users — ADR-011
- [x] Admin broadcast to all bot users from `/admin` — ADR-017
- [x] 24-hour reminder to registered participants — ADR-013
- [x] Shareable deep-link per event — ADR-010

### Already shipped (post-planning)

- [x] **Hide past events from active UI** — past calendar dates hidden from home list, «Мои регистрации», ticket counter, and admin manage list; rows kept in DB. See ADR-018.
- [x] **T-207 Registration +1 (party_size)** — ADR-019 — [ticket](tickets/T-207-registration-plus-one.md)

### Already shipped (post-planning, continued)

- [x] **T-208 Access groups** — ADR-020 — [ticket](tickets/T-208-access-groups.md)

### Backlog

- [ ] **T-201 Access codes** — blocked; will join `group_memberships` after codes ADR (see ADR-020) — [ticket](tickets/T-201-access-codes.md)
- [ ] **T-202 Propose your own event** — blocked on ADR-016 — [ticket](tickets/T-202-propose-event.md)
- [ ] **T-203 Past events status / archive** — [ticket](tickets/T-203-past-events-archive.md)
- [ ] **T-204 Event categories and filters** — needs ADR — [ticket](tickets/T-204-event-categories.md)
- [ ] **T-205 English localization** — needs ADR — [ticket](tickets/T-205-english-i18n.md)
- [ ] **T-206 Analytics dashboard** — needs ADR — [ticket](tickets/T-206-analytics-dashboard.md)

---

## Iteration 3

> Detailed requirements in `docs/decisions/014-event-ownership-and-inline-editing.md`.  
> Tickets: [`docs/tickets/`](tickets/).

- [ ] **T-301 Event ownership & in-app admin editing** — split before factory enqueue — [ticket](tickets/T-301-event-ownership-editing.md)
- [ ] **T-302 Event duplication** — [ticket](tickets/T-302-event-duplication.md)
- [ ] **T-303 Invite system** — blocked on ADR — [ticket](tickets/T-303-invite-system.md)
- [ ] **T-304 Web version** — blocked on ADR — [ticket](tickets/T-304-web-version.md)