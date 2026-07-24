# T-202 — Propose your own event


## Human summary (review this first)

**Will do:**
- (Later) Let users propose events; admin approves or rejects

**Will not do:**
- Anything until ADR-016 exists

**Touched areas:** Mini App + admin moderation (future)

**Risk:** High without ADR — **blocked**

**Smoke check after merge:** N/A

**Reviewer decision:** `[ ] Approved to implement` — blocked on ADR-016

---

| Field | Value |
|-------|-------|
| ID | T-202 |
| Title | User event proposals with admin approve/reject |
| Status | `blocked` |
| Spec / ADR | ADR-016 (**to be written**) — not DoR |
| App | `zarya-tg` |
| Estimate | L (split after ADR) |

## Goal

Any registered user can submit an event proposal; admin approves (publish + announce) or rejects (delete draft).

## Acceptance Criteria

- [ ] Draft ADR-016 covering: draft model fields, Mini App proposal UI, admin approve/reject flows, announcement on publish
- [ ] Only then: split into implement tickets with concrete AC

## Out of Scope

- Public web proposals
- Paid featured listings

## Implementation Notes

- Blocked on ADR-016. Not factory-ready.
