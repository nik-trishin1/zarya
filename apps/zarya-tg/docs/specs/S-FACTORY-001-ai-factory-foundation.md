# S-FACTORY-001 — AI-Factory foundation for zarya

## Human summary (review this first)

**In plain language, we will:**
- Introduce a reusable “AI-Factory” playbook at the monorepo root (`process/`) that any future zarya app can copy
- Require every spec and ticket to start with a short **Human summary** you can approve before an agent writes code
- Add CI that runs tests/lint/build and can scan Railway logs for runtime errors
- Keep product tickets for zarya-tg in `apps/zarya-tg/docs/tickets/`, not inside the portable pack

**We will not:**
- Change how events, registration, or the admin bot work in this foundation pass
- Force Railway credentials on every contributor fork (scan skips if unset)

**User-visible outcome:**
- None directly in the Mini App. Developers/agents get clearer gates and you get readable specs to review.

**Main risks / open questions already decided:**
- Portable pack lives at `process/` (not under a single app)
- Orchestrator = Cursor Automations (documented), not a custom service
- Railway log scan is best-effort when secrets exist; skip when missing

**How we will know it worked (smoke):**
- New PR shows CI jobs; opening a ticket template shows Human summary; `process/README.md` describes copy-to-another-repo

**Reviewer decision:** `[x] Approved for ticket split` · Reviewer: factory-pilot · Date: 2026-07-24

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-FACTORY-001 |
| Title | AI-Factory foundation |
| Status | `approved` |
| Related ADR / PRD | Process only (no product ADR) |
| Owner | zarya maintainers |

## Problem

The repo already practices AI-assisted work (PRD, ADRs, markdown tasks) but lacks machine gates, portable templates, and human-readable pre-implementation summaries needed for unattended factory execution.

## Goals

- Portable process pack
- Human-reviewable specs/tickets
- CI + Railway log awareness
- Clear review gate and orchestrator docs

## Non-goals

- Product Iteration 2/3 features
- Custom orchestrator product

## Proposed behavior

See `process/ai-factory/` and tickets T-FACTORY-001 / T-FACTORY-002.

## Acceptance criteria (spec-level)

- [x] Portable `process/` tree exists
- [x] Human summary required in spec/ticket templates
- [x] CI workflow includes tests, lint/build, Railway scan script
- [x] zarya ticket index links open backlog items

## Open questions

None for this foundation pass.
