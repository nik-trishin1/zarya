# T-202 — Propose your own event


## Human summary (review this first)

**Will do:**
- Nothing in product for now — **deferred** per [ADR-016](../decisions/016-defer-user-event-proposals.md)
- Concierge path only: participants message the admin; admin creates events via existing `/admin` FSM

**Will not do:**
- Mini App proposal form
- Draft event / proposal entities
- Approve/reject publish pipeline (options B/C)

**Touched areas:** Docs only (ADR-016 + backlog)

**Risk:** None for product code

**Smoke check after merge:** N/A

**Reviewer decision:** Product path deferred until clear demand — see ADR-016 (2026-09-16)

---

| Field | Value |
|-------|-------|
| ID | T-202 |
| Title | User event proposals with admin approve/reject |
| Status | `cancelled` |
| Spec / ADR | [ADR-016](../decisions/016-defer-user-event-proposals.md) (Accepted — defer product / concierge A) |
| App | `zarya-tg` |
| Estimate | — |

## Goal

~~Any registered user can submit an event proposal; admin approves (publish + announce) or rejects (delete draft).~~

**Cancelled / deferred until demand (2026-09-16):** Keep concierge (message admin). Do not build Mini App form, drafts, or approve/reject. Revisit only if there is clear demand for “create my own events.” ADR-014 / T-301 stay separate.

## Acceptance Criteria

- [x] ADR-016 records deferral (concierge A; non-goals B/C; revisit on demand)
- [x] Ticket + backlog marked cancelled with deferred-until-demand rationale
- [ ] ~~Draft ADR-016 covering full draft model + Mini App UI + approve/reject~~ (not now)
- [ ] ~~Split into implement tickets~~ (only if ADR revisits)

## Out of Scope

- Public web proposals
- Paid featured listings
- Product options B and C until demand justifies a new ADR

## Implementation Notes

- Repo has no `deferred` status; use `cancelled` with explicit “deferred until demand” (same pattern as T-205).
- Not factory-ready. No product code.
