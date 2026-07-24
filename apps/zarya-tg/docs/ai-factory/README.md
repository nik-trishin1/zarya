# AI-Factory (zarya-tg)

Project notes for the factory process. **Portable standards live in** [`process/ai-factory/`](../../../../process/ai-factory/).

| Doc | Location |
|-----|----------|
| Playbook | `process/ai-factory/README.md` |
| Spec template (Human summary) | `process/ai-factory/SPEC_TEMPLATE.md` |
| Ticket template | `process/ai-factory/TICKET_TEMPLATE.md` |
| DoR | `process/ai-factory/DEFINITION_OF_READY.md` |
| Review pass | `process/ai-factory/REVIEW_PASS.md` |
| Orchestrator | `process/ai-factory/ORCHESTRATOR.md` |
| CI + Railway logs | `process/ai-factory/CI.md` |
| zarya tickets | [`../tickets/`](../tickets/) |
| Pilot review | [`PILOT_REVIEW.md`](PILOT_REVIEW.md) |

## Operator next steps

1. GitHub secrets/vars for Railway log scan (see `docs/deploy-railway.md` → CI section).
2. Create Cursor Automation `factory-implement` using the prompt in `process/ai-factory/ORCHESTRATOR.md`.
3. Only enqueue tickets whose Human summary is approved and DoR is green.
