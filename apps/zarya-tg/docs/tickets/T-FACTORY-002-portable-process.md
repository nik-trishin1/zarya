# T-FACTORY-002 — Portable AI-Factory process + human-readable specs

## Human summary (review this first)

**Will do:**
- Put reusable AI-Factory standards under top-level `process/` so other repos can copy them
- Require a plain-language **Human summary** on specs and tickets for human review before coding
- Document orchestrator setup, review pass, DoR, and Cursor rules
- Convert open zarya backlog items into ticket files that point at the portable templates

**Will not do:**
- Build a custom orchestrator binary
- Auto-create Cursor Automations in the dashboard (documented for an operator)
- Implement Iteration 2/3 product features

**Touched areas (plain language):**
- Process docs, Cursor rules, ticket index, agent instructions

**Risk:** Low — documentation/process only

**Smoke check after merge:**
- `process/README.md` explains how to reuse in another project; a new ticket can be created from the portable template with a Human summary

**Reviewer decision:** `[x] Approved to implement` · Reviewer: factory-pilot · Date: 2026-07-24

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-FACTORY-002 |
| Title | Portable AI-Factory process + human-readable specs |
| Status | `done` |
| Spec / ADR | [S-FACTORY-001](../specs/S-FACTORY-001-ai-factory-foundation.md) |
| Estimate | M |

## Goal

Establish a portable, human-reviewable process so zarya (and future apps) can run AI-Factory without reinventing templates.

## Acceptance criteria

- [x] `process/ai-factory/` contains portable templates (spec, ticket, DoR, review, orchestrator, CI)
- [x] Spec and ticket templates include mandatory **Human summary** for reviewer approval
- [x] Cursor rules `ai-factory.mdc` and `review-gate.mdc` installed; copies kept under `process/cursor-rules/`
- [x] zarya tickets live under `apps/zarya-tg/docs/tickets/` and reference portable templates
- [x] `AGENTS.md` / `tasks.md` point at the new process

## Out of scope

- Linear/Notion sync
- Enabling Automations in Cursor UI (operator checklist only)

## Verification

1. [x] Files present under `process/`
2. [x] Pilot tickets T-FACTORY-001/002 use Human summary
3. [ ] CI green on PR
4. [x] Review pass via factory pilot notes
