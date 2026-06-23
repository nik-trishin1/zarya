# zarya — Agent Instructions

This repository contains the full source code, product documentation, and design assets for **zarya**, a Telegram Mini App for community event management.

## Session Startup

At the start of every session, read the following files before taking any action:

- `README.md` — project overview and architecture
- `docs/prd.md` — Product Requirements Document (source of truth for features and scope)
- `docs/decisions/` — all architectural and product decisions made so far
- `docs/tasks.md` — current task backlog and status

## Repository Structure

| Path | Purpose |
|------|---------|
| `frontend/` | React + TypeScript Telegram Mini App |
| `backend/` | FastAPI backend + aiogram Telegram bot |
| `docs/prd.md` | Product Requirements Document v4.0 |
| `docs/tasks.md` | Task backlog |
| `docs/decisions/` | Decision records (ADRs) |
| `docs/research/` | UX analysis, benchmarks, competitor research |
| `docs/deliverables/` | Finalized artifacts (mockups, exports) |
| `docs/assets/` | Images and design assets |
| `.cursor/rules/` | AI agent behavior rules |
| `.cursor/skills/` | Reusable agent skills for this project |

## Source of Truth

- **Product scope:** `docs/prd.md` is the canonical source for what is in and out of MVP.
- **Architecture decisions:** `docs/decisions/` contains all ADRs; do not contradict them without creating a new decision record.
- **Tasks:** `docs/tasks.md` tracks current work; update it when completing or adding tasks.

## Language

- Code: English (variable names, comments, commit messages).
- User-facing content: Russian (UI text, bot messages).
- Documentation: English.

## Commit Convention

Follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
Keep commits atomic and descriptive.
