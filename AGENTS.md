# zarya — Agent Instructions

Monorepo for the **zarya** community platform. Apps: `apps/zarya-tg/` (Telegram Mini App MVP), `apps/link-qr/`. Always-on: `.cursor/rules/zarya-core.mdc` + `anti-bias.mdc`.

## Focus (update when it changes)

- **Now:** process / agent-context optimization + launch ops (`apps/zarya-tg/docs/launch-ops-checklist.md`).
- **Ask first:** Railway secrets and variables, Telegram bot webhook, production DB schema.
- **Deferred:** T-304 (public web version). T-301/T-302/T-303/T-201 wait for a Human summary approve or ADR (`tasks.md`).

## Session Startup

Read before acting:

1. `apps/zarya-tg/docs/tasks.md` — active queue (done history: `tasks-archive.md`)
2. The **assigned ticket** under `apps/zarya-tg/docs/tickets/`, plus the spec/ADR it links

Open on demand: `prd.md`, other tickets/ADRs when the ticket or a conflict points there. Large product hypothesis → `.cursor/rules/next-move-theory.mdc` → `.cursor/skills/product-hypothesis/SKILL.md` (skip for factory tickets, bugfixes, approved specs).

## Layout

`process/` portable AI-Factory (+ `process/next-move-theory/`) · `apps/zarya-tg/{frontend,backend}` · `apps/zarya-tg/docs/{tickets,specs,decisions,deliverables,research/nmt,handoffs}` · `Next-Move-Theory-Canon/` · `.cursor/{rules,skills}` · `.github/workflows/ci.yml`

## Where truth lives

- **Scope / AC:** `apps/zarya-tg/docs/prd.md` + ADRs in `docs/decisions/`
- **Process:** `process/ai-factory/` — tickets stay under `apps/zarya-tg/docs/tickets/`; NMT output is a hypothesis, not DoR
- **Third-party skills:** `process/ai-factory/SKILL_INSTALL.md` (preferred scan `skillspector … --no-llm`; refresh Project store `docs/skills-knowledge.md` after install/remove/rename)
- **Followthrough** (user-visible product claims): `process/ai-factory/FOLLOWTHROUGH.md` → Project store `docs/followthrough/<change-id>.md`
- **Workflow skills** (`grill-me`, `handoff`, `to-questionnaire`, `writing-for-agents`): `.cursor/skills/matt-pocock-productivity/README.md` — `grill-me` before DoR only; never on factory-queued tickets
