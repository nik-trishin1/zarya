# zarya — Agent Instructions

This repository is a monorepo for the **zarya** community platform. It currently contains one app and is structured to accommodate additional apps in the future.

## Session Startup

At the start of every session, read the following files before taking any action:

- `README.md` — repository overview and app index
- `process/README.md` — portable AI-Factory process (cross-project)
- `apps/zarya-tg/docs/prd.md` — Product Requirements Document (source of truth for zarya-tg features and scope)
- `apps/zarya-tg/docs/tasks.md` — current task backlog and status
- `apps/zarya-tg/docs/tickets/` — AC tickets with Human summaries
- `apps/zarya-tg/docs/decisions/` — all architectural and product decisions

## Repository Structure

| Path | Purpose |
|------|---------|
| `process/` | **Portable** AI-Factory standards (copy to other repos) |
| `apps/zarya-tg/` | Telegram Mini App (MVP) |
| `apps/zarya-tg/frontend/` | React + TypeScript Telegram Mini App |
| `apps/zarya-tg/backend/` | FastAPI backend + aiogram Telegram bot |
| `apps/zarya-tg/docs/prd.md` | Product Requirements Document |
| `apps/zarya-tg/docs/tasks.md` | Task backlog index |
| `apps/zarya-tg/docs/tickets/` | Project tickets (Human summary + AC) |
| `apps/zarya-tg/docs/specs/` | Project feature specs (Human summary first) |
| `apps/zarya-tg/docs/decisions/` | Architecture Decision Records (ADRs) |
| `apps/zarya-tg/docs/deliverables/` | UI mockups and finalized artifacts |
| `apps/zarya-tg/docs/research/` | UX analysis, benchmarks |
| `.cursor/rules/` | Cursor AI behavior rules (includes copies from `process/cursor-rules/`) |
| `.github/workflows/ci.yml` | PR gates: pytest, lint/build, Railway log scan |

## Source of Truth

**Product scope:** `apps/zarya-tg/docs/prd.md` is the canonical source for what is in and out of MVP. Do not implement features outside this scope without creating a new decision record.

**Architecture decisions:** `apps/zarya-tg/docs/decisions/` contains all ADRs. Do not contradict them without creating a new record.

**Process:** `process/ai-factory/` is the portable factory playbook. Project tickets stay under `apps/zarya-tg/docs/tickets/`.

**Tasks:** `apps/zarya-tg/docs/tasks.md` indexes work; detailed AC live in ticket files.

## Language

Code, comments, commit messages, and documentation are written in English. User-facing UI text and bot messages are in Russian.

## Agent Rules Index

| Rule file | Type | Purpose |
|-----------|------|--------|
| `zarya-context.mdc` | Always Apply | Monorepo context and MVP scope |
| `ai-factory.mdc` | Always Apply | Factory DoR, Human summary, CI/review gates |
| `review-gate.mdc` | Always Apply | Separate review pass after implementation |
| `clarify-before-action.mdc` | Always Apply | Ask before uncertain actions (factory exception documented) |
| `self-check.mdc` | Always Apply | Verify output before finalizing |
| `anti-bias.mdc` | Always Apply | Check for cognitive biases |
| `git-hygiene.mdc` | Always Apply | Commit and branch conventions |
| `handoff-summary.mdc` | Apply Intelligently | Produce session handoff notes |
| `context-management.mdc` | Apply Intelligently | Manage context budget |
| `spec-driven-dev.mdc` | Apply Intelligently | Plan before coding |

## Commit Convention

Follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`. Keep commits atomic and descriptive. Scope the commit to the app when relevant, e.g. `feat(zarya-tg): add event registration endpoint`. Reference ticket IDs when applicable (`T-203`).
