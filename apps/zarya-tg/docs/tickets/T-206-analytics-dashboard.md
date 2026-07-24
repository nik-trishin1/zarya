# T-206 — Analytics dashboard (admin)


## Human summary (review this first)

**Will do:**
- (After ADR) Give admin counts: registrations per event, active users, monthly events

**Will not do:**
- Public analytics or third-party SDKs

**Touched areas:** Admin-only API or bot view

**Risk:** Medium — metric definitions must be fixed in ADR

**Smoke check after merge:** Admin sees numbers; non-admin denied

**Reviewer decision:** `[ ] Approved to implement` — needs ADR first

---

| Field | Value |
|-------|-------|
| ID | T-206 |
| Title | Admin analytics: registrations, active users, monthly events |
| Status | `todo` |
| Spec / ADR | Needs ADR (metrics definitions + delivery channel: Mini App vs bot) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Admin can see total registrations per event, active users, and monthly event count.

## Acceptance Criteria

- [ ] ADR defines “active user” and timezones for “monthly”
- [ ] Admin-only endpoint or bot view returns: registrations per event, active user count, events created this month
- [ ] Unauthorized users receive 403 / bot denial
- [ ] Backend tests for aggregation queries
- [ ] Russian labels in any user-facing admin UI

## Out of Scope

- Public analytics
- Third-party product analytics SDKs

## Implementation Notes

- Blocked on ADR. Not DoR for factory until written.
