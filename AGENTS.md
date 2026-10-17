# zarya — Agent Instructions

Monorepo for the **zarya** community platform. Apps: `apps/zarya-tg/` (Telegram Mini App MVP), `apps/link-qr/`.

## Focus (update when it changes)

- **Now:** process / agent-context optimization + launch ops (`apps/zarya-tg/docs/launch-ops-checklist.md`).
- **Ask first:** Railway secrets and variables, Telegram bot webhook, production DB schema.
- **Deferred:** T-304 (public web version). T-301/T-302/T-303/T-201 wait for a Human summary approve or ADR (`tasks.md`).

## Session Startup

Read before acting:

1. `README.md` — app index
2. `process/README.md` — AI-Factory process
3. `apps/zarya-tg/docs/tasks.md` — active queue (done history: `tasks-archive.md`)
4. The **assigned ticket** under `apps/zarya-tg/docs/tickets/`, plus the spec/ADR it links

Open on demand: `prd.md` (scope or AC questions), other tickets, other ADRs in `apps/zarya-tg/docs/decisions/` (only when the ticket or a conflict points there). MVP guardrails: `.cursor/rules/zarya-context.mdc`.

Large product hypothesis (new segment/Job, value proposition, positioning, "should we build this", live-product diagnosis): follow `.cursor/rules/next-move-theory.mdc` → `.cursor/skills/product-hypothesis/SKILL.md`. Skip it for factory tickets, bugfixes, approved specs.

## Layout

`process/` portable AI-Factory (+ `process/next-move-theory/`) · `apps/zarya-tg/{frontend,backend}` · `apps/zarya-tg/docs/{tickets,specs,decisions,deliverables,research/nmt,handoffs}` · `Next-Move-Theory-Canon/` vendored canon · `.cursor/{rules,skills}` · `.github/workflows/ci.yml` PR gates.

## Source of Truth

- **Scope:** `apps/zarya-tg/docs/prd.md`; nothing outside it without a decision record.
- **Architecture:** `apps/zarya-tg/docs/decisions/` ADRs; do not contradict without a new record.
- **Process:** `process/ai-factory/` playbook; tickets stay under `apps/zarya-tg/docs/tickets/`. NMT output is a hypothesis, not Definition of Ready.
- **Third-party skills:** `process/ai-factory/SKILL_INSTALL.md`.
- **Workflow skills** (`grill-me`, `handoff`, `to-questionnaire`, `writing-for-agents`): `.cursor/skills/matt-pocock-productivity/README.md`. Run `grill-me` before DoR only; never on factory-queued tickets.

## Language and commits

Code, comments, commit messages, docs in English; UI and bot messages in Russian. Conventional commits scoped to the app (`feat(zarya-tg): …`), with ticket ID when applicable (`T-203`); rules in `.cursor/rules/git-hygiene.mdc`.
