# Portable process standards

This directory holds **project-agnostic** AI development process artifacts.
Copy or submodule it into any repo to get the same AI-assisted → AI-Factory workflow.

| Path | Purpose |
|------|---------|
| [`ai-factory/`](ai-factory/) | Specs, tickets, DoR, review gate, orchestrator, CI expectations |
| [`ai-factory/scripts/`](ai-factory/scripts/) | Portable CI helpers (e.g. Railway log scan) |
| [`next-move-theory/`](next-move-theory/) | How to vendor and use Next Move Theory for large product hypotheses |
| [`cursor-rules/`](cursor-rules/) | Cursor `.mdc` rules to copy into `.cursor/rules/` |

Workflow productivity skills (grill / handoff / questionnaire / writing-for-agents) live under [`.cursor/skills/`](../.cursor/skills/) with adopt/skip notes in [`.cursor/skills/matt-pocock-productivity/README.md`](../.cursor/skills/matt-pocock-productivity/README.md). They are project-wired adaptations, not a portable `process/` package.

## Adopt in another project

1. Copy `process/` to the new repo root (or keep as a shared package).
2. Copy `process/cursor-rules/*.mdc` into `.cursor/rules/`.
3. For large product hypotheses, install Next Move Theory per [`next-move-theory/README.md`](next-move-theory/README.md) (canon at repo root, skills under `.cursor/skills/`).
4. Wire CI from [`ai-factory/CI.md`](ai-factory/CI.md) (tests + optional Railway log scan).
5. Keep **project tickets and specs** under the app/docs tree; only templates and rules stay here.

Project-specific content (PRD, ADRs, concrete tickets) must **not** live under `process/`.
