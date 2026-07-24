# Definition of Ready (portable)

A ticket may enter the AI-Factory queue only when **all** items below are true.

## Required

1. **Stable ID and title** in the project ticket tree.
2. **Linked approved spec or ADR** — enough detail to implement without product questions.
3. **Human summary** on the ticket — reviewed and marked approved (or explicitly waived with reason).
4. **Acceptance criteria** — ≥2 checkboxes; each verifiable by test, lint, or one-step smoke.
5. **Out of scope** written.
6. **Single PR size** — split before queueing if larger.
7. **No open product questions** — if an agent would ask “which behavior?”, it is not Ready.
8. **Verification plan** — which CI jobs apply (unit/lint/build/Railway logs).

## Not Ready

- Checkbox-only backlog lines without AC or Human summary
- “ADR/spec to be written”
- Vague goals without measurable outcome
- Tickets needing secrets/production access the agent does not have

## Factory mode vs clarify-before-action

When DoR is satisfied and the ticket is factory-queued, the agent:

- Chooses a **safe default** consistent with the approved spec/ADR for minor gaps
- Documents the choice in the PR body under “Defaults chosen”
- Does **not** stop mid-flight unless the change would violate the spec/ADR or expand scope
