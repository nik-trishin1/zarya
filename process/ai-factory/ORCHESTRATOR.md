# Orchestrator setup (portable)

Send DoR-ready tickets to Cursor Cloud Agents / Automations; receive PRs without mid-flight chat.

## Automation: implement

**Suggested name:** `factory-implement`

**Trigger:** issue/PR label `factory-ready`, Linear status, or manual Cloud Agent with ticket path.

**Prompt:**

```text
You are executing an AI-Factory ticket. Work unattended until the PR is ready.

1. Read AGENTS.md (or repo agent guide), the ticket file, and linked spec/ADR.
2. Confirm Definition of Ready (process/ai-factory/DEFINITION_OF_READY.md). If not Ready, stop and report what is missing.
3. If Ready: implement only this ticket. Prefer safe defaults consistent with the approved Human summary / spec; document choices in the PR. Do not expand scope.
4. Create a feature branch per repo convention.
5. Run the verification steps listed on the ticket and in process/ai-factory/CI.md.
6. Commit with conventional commits, push, open/update a draft PR (use repo PR template if present).
7. Set ticket status to in_review and paste the review prompt from process/ai-factory/REVIEW_PASS.md.
8. Do not merge. Do not ask mid-flight questions unless the change would violate the spec/ADR.

Ticket path: {{TICKET_PATH}}
```

## Automation: review (optional)

**Suggested name:** `factory-review` — runs `REVIEW_PASS.md` prompt only.

## Operator checklist

- [ ] Create implement Automation in Cursor dashboard with the prompt above
- [ ] Cloud environment has the same runtimes CI uses
- [ ] GitHub Actions enabled; secrets for Railway log scan configured if used
- [ ] Dry-run on one pilot ticket before bulk queueing

## Success metric

% of factory tickets that reach a green PR **without** a human message mid-flight.
