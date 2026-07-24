# AI-Factory (portable)

Process standard for moving from AI-assisted coding to an unattended ticket factory.
Project-agnostic: copy this folder; keep PRD/ADRs/tickets in the consuming app.

## Human review first

Every **spec** and every **ticket** must include a **Human summary** section written for a non-implementing reviewer:

- What will change for users / the system
- What will *not* change
- Main risks
- Suggested verification the reviewer can understand without reading the diff

Humans review that summary **before** enqueueing implementation. Agents treat an approved summary as the contract.

## Artifacts

| File | Role |
|------|------|
| [`SPEC_TEMPLATE.md`](SPEC_TEMPLATE.md) | Feature/spec template with mandatory Human summary |
| [`TICKET_TEMPLATE.md`](TICKET_TEMPLATE.md) | Atomic ticket (≤1 PR) with AC + Human summary |
| [`DEFINITION_OF_READY.md`](DEFINITION_OF_READY.md) | Gate before factory queue |
| [`REVIEW_PASS.md`](REVIEW_PASS.md) | Separate post-implement review |
| [`ORCHESTRATOR.md`](ORCHESTRATOR.md) | Cursor Automation / Cloud Agent wiring |
| [`CI.md`](CI.md) | Required CI gates including optional Railway log scan |
| [`scripts/check-railway-logs.sh`](scripts/check-railway-logs.sh) | Portable Railway deploy/HTTP log scanner |

## Happy path

1. Roast idea → write spec from `SPEC_TEMPLATE.md` → **human reviews Human summary**.
2. Split into DoR tickets from `TICKET_TEMPLATE.md`.
3. Enqueue via orchestrator (`ORCHESTRATOR.md`).
4. Agent implements → local checks → PR.
5. CI green (tests + lint/build + Railway log scan when configured).
6. Separate review pass → human merges.
