# Review pass (portable)

After implementation and before merge, run a **separate** review that is not the same chat that wrote the code.

## Why

Same-session self-review misses AC gaps and regressions. Level 2/3 requires an explicit review gate.

## How (pick one)

1. **Second agent** — new session with the prompt below (preferred).
2. **Bugbot** — if enabled on the PR.
3. **Human** — always owns final merge / product smoke.

## Review agent prompt

```text
Review this PR against the ticket acceptance criteria and Human summary only.

Ticket path: <path-to-T-NNN.md>
Spec/ADR: <path>
PR: branch vs main

Checks:
1. Does every acceptance criterion hold?
2. Does the diff match the Human summary (no silent scope creep)?
3. Any obvious regressions in core flows?
4. Are user-facing strings in the product language? Comments in English (if that is the repo rule)?
5. Are tests/lint/CI adequate?
6. If Railway log scan ran — any new runtime errors related to this change?

Reply with: PASS / FAIL, findings, and required fixes before merge.
Do not implement fixes unless asked.
```

## Clean slate and verified findings

- **Clean slate.** "Works on the author's machine" is not shipped. Reviewers run checks from a fresh checkout (new cloud agent or CI), not the implementer's working tree or env.
- **Verify, don't rubber-stamp.** Every reviewer finding (agent, Bugbot, or human) is reproduced by execution (test, command, log) or disproven with evidence before it is accepted or dismissed. Unverified findings are noted as such and do not block merge on their own.
- **Reflect.** If the same correction appears in two reviews, update a rule or skill (see `SKILL_INSTALL.md` step 6), not only the chat.

## Rule

Implementation agents set ticket status to `in_review` and request this pass.
Do not mark `done` until review is PASS and CI is green.
