# T-201 — Access codes for zarya + circle events


## Human summary (review this first)

**Will do:**
- (Later) Let admin issue personal codes that unlock circle-tier events

**Will not do:**
- Anything until ADR-015 exists

**Touched areas:** Product/access control (future)

**Risk:** High if started without ADR — **blocked**

**Smoke check after merge:** N/A until unblocked

**Reviewer decision:** `[ ] Approved to implement` — blocked on ADR-015

---

| Field | Value |
|-------|-------|
| ID | T-201 |
| Title | Access codes for circle-tier events |
| Status | `blocked` |
| Spec / ADR | ADR-015 (**to be written**) — not DoR |
| App | `zarya-tg` |
| Estimate | L (split after ADR) |

## Goal

Allow admin-issued personal access codes to unlock **group membership** (same `group_memberships` rows as ADR-020), not a parallel ACL.

## Acceptance Criteria

- [ ] Draft codes ADR extending ADR-020: code generation, storage, revoke, redemption UX → `group_memberships.source=access_code`
- [ ] Only then: implement per ADR (split into follow-up tickets)

## Out of Scope

- Payment / subscriptions
- Automatic code expiry (unless ADR says otherwise)

## Implementation Notes

- Blocked on ADR-015. Do **not** enqueue for factory until ADR exists and this ticket is rewritten with concrete AC.
