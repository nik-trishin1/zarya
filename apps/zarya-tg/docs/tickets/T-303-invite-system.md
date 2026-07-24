# T-303 — Invite system


## Human summary (review this first)

**Will do:**
- (Later) Unique invite links with inviter attribution for admin

**Will not do:**
- Work before an invite ADR exists

**Risk:** Blocked without ADR

**Reviewer decision:** `[ ] Approved to implement` — blocked

---

| Field | Value |
|-------|-------|
| ID | T-303 |
| Title | Unique invite links with inviter attribution |
| Status | `blocked` |
| Spec / ADR | Needs ADR |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Each user gets a unique invite link; admin can see who invited whom.

## Acceptance Criteria

- [ ] ADR covers token format, attribution on first start, admin listing, abuse cases
- [ ] Follow-up implement tickets only after ADR

## Out of Scope

- Referral rewards / payments

## Implementation Notes

- Not factory-ready.
