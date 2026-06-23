# zarya — Agent Instructions

This repository is a monorepo for the **zarya** community platform. It currently contains one app and is structured to accommodate additional apps in the future.

## Session Startup

At the start of every session, read the following files before taking any action:

- `README.md` — repository overview and app index
- `apps/zarya-tg/docs/prd.md` — Product Requirements Document (source of truth for zarya-tg features and scope)
- `apps/zarya-tg/docs/tasks.md` — current task backlog and status
- `apps/zarya-tg/docs/decisions/` — all architectural and product decisions

## Repository Structure

| Path | Purpose |
|------|---------|
| `apps/zarya-tg/` | Telegram Mini App (MVP) |
| `apps/zarya-tg/frontend/` | React + TypeScript Telegram Mini App |
| `apps/zarya-tg/backend/` | FastAPI backend + aiogram Telegram bot |
| `apps/zarya-tg/docs/prd.md` | Product Requirements Document |
| `apps/zarya-tg/docs/tasks.md` | Task backlog |
| `apps/zarya-tg/docs/decisions/` | Architecture Decision Records (ADRs) |
| `apps/zarya-tg/docs/deliverables/` | UI mockups and finalized artifacts |
| `apps/zarya-tg/docs/research/` | UX analysis, benchmarks |
| `.cursor/rules/` | AI agent behavior rules |

## Source of Truth

**Product scope:** `apps/zarya-tg/docs/prd.md` is the canonical source for what is in and out of MVP. Do not implement features outside this scope without creating a new decision record.

**Architecture decisions:** `apps/zarya-tg/docs/decisions/` contains all ADRs. Do not contradict them without creating a new record.

**Tasks:** `apps/zarya-tg/docs/tasks.md` tracks current work. Update it when completing or adding tasks.

## Language

Code, comments, commit messages, and documentation are written in English. User-facing UI text and bot messages are in Russian.

## Commit Convention

Follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`. Keep commits atomic and descriptive. Scope the commit to the app when relevant, e.g. `feat(zarya-tg): add event registration endpoint`.
