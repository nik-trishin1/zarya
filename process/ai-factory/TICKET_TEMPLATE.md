# Ticket template (portable)

Copy to the project ticket tree, e.g. `docs/tickets/T-NNN-short-slug.md`.
A ticket is not Ready until [`DEFINITION_OF_READY.md`](DEFINITION_OF_READY.md) is satisfied.

---

## Human summary (review this first)

> Short enough to approve in one glance. Reviewers should understand the change without opening the code.

**Will do:**
- …

**Will not do:**
- …

**Touched areas (plain language):**
- e.g. “event list API”, “registration button”, “admin bot create flow”

**Risk:**
- Low / Medium / High — one sentence why

**Smoke check after merge:**
- …

**Reviewer decision:** `[ ] Approved to implement` · `[ ] Needs changes` · Reviewer: ____ · Date: ____

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-NNN |
| Title | Short imperative title |
| Status | `todo` \| `in_progress` \| `in_review` \| `done` \| `blocked` |
| Spec / ADR | Link |
| Estimate | S / M / L (one PR max; split if larger) |

## Goal

One sentence.

## Acceptance criteria

- [ ] Observable, testable criterion 1
- [ ] Observable, testable criterion 2
- [ ] Observable, testable criterion 3

## Out of scope

- …

## Implementation notes (for agents)

- Key files / modules
- Constraints from ADR/spec
- Suggested automated tests

## Verification (agents)

1. [ ] Project test suite for touched layer(s)
2. [ ] Lint / typecheck / build as required by repo CI
3. [ ] CI green on the PR (including Railway log scan when enabled)
4. [ ] Separate review pass requested ([`REVIEW_PASS.md`](REVIEW_PASS.md))

## Handoff (when done)

- PR URL:
- Defaults chosen (if any):
- Residual risks:
