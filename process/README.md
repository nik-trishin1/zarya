# Portable process standards

This directory holds **project-agnostic** AI development process artifacts.
Copy or submodule it into any repo to get the same AI-assisted → AI-Factory workflow.

| Path | Purpose |
|------|---------|
| [`ai-factory/`](ai-factory/) | Specs, tickets, DoR, review gate, orchestrator, CI expectations |
| [`ai-factory/scripts/`](ai-factory/scripts/) | Portable CI helpers (e.g. Railway log scan) |
| [`cursor-rules/`](cursor-rules/) | Cursor `.mdc` rules to copy into `.cursor/rules/` |

## Adopt in another project

1. Copy `process/` to the new repo root (or keep as a shared package).
2. Copy `process/cursor-rules/*.mdc` into `.cursor/rules/`.
3. Wire CI from [`ai-factory/CI.md`](ai-factory/CI.md) (tests + optional Railway log scan).
4. Keep **project tickets and specs** under the app/docs tree; only templates and rules stay here.

Project-specific content (PRD, ADRs, concrete tickets) must **not** live under `process/`.
