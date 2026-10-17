# zarya — Task Backlog

> Refreshed 2026-10-17. Done history: [`tasks-archive.md`](tasks-archive.md). Tickets: [`docs/tickets/`](tickets/). Process: [`process/ai-factory/`](../../../process/ai-factory/).

## Status Legend

`[ ]` Not started · `[~]` In progress · `[x]` Done · `[-]` Blocked / cancelled

**DoR** = Definition of Ready (`process/ai-factory/DEFINITION_OF_READY.md`): approved Human summary + linked ADR/spec + verifiable AC.

---

## Open backlog (review this)

Ordered for product triage — not a factory queue. Nothing below is factory-ready until DoR = yes.

### Ready for factory (DoR met)

| ID | Title | Notes | Links |
|----|-------|-------|-------|

### Low priority (later)

| ID | Title | Notes | Links |
|----|-------|-------|-------|
| **T-212** | Almost-full nudge for maybe RSVPs | When seats nearly gone, DM maybe users («Места почти закончились — присоединяйся»). Deferred capacity urgency from T-211. | backlog stub below |

### Needs Human summary approve (ADR exists)

| ID | Title | Blocker | Links |
|----|-------|---------|-------|
| **T-302** | Admin event duplication | Approve (may need thin ADR addendum) | [ticket](tickets/T-302-event-duplication.md) · [ADR-014](decisions/014-event-ownership-and-inline-editing.md) |

### Needs split / more design before enqueue

| ID | Title | Blocker | Links |
|----|-------|---------|-------|
| **T-301** | Event ownership + in-app admin editing | Split into child tickets; ADR-014 exists | [ticket](tickets/T-301-event-ownership-editing.md) · [ADR-014](decisions/014-event-ownership-and-inline-editing.md) |

### Needs ADR (not Ready)

| ID | Title | Missing | Links |
|----|-------|---------|-------|
| **T-204** | Event categories + filter chips | Category ADR | [ticket](tickets/T-204-event-categories.md) |
| **T-206** | Admin analytics dashboard | Metrics + channel ADR | [ticket](tickets/T-206-analytics-dashboard.md) |
| **T-201** | Access codes (circle tier) | ADR-015 (after ADR-020 groups) | [ticket](tickets/T-201-access-codes.md) |
| **T-303** | Invite system | Invite ADR | [ticket](tickets/T-303-invite-system.md) |
| **T-304** | Public web version (zarya.org) | Web ADR; **deferred** (not this iteration) | [ticket](tickets/T-304-web-version.md) |

### Cancelled

| ID | Title | Reason | Links |
|----|-------|--------|-------|
| **T-202** | Propose your own event | Deferred until demand — concierge A (ADR-016); no Mini App form / drafts / approve pipeline | [ticket](tickets/T-202-propose-event.md) · [ADR-016](decisions/016-defer-user-event-proposals.md) |
| **T-205** | English i18n | Russian-only (ADR-003) | [ticket](tickets/T-205-english-i18n.md) |

### Ops / launch (Phase 4 leftovers)

Tracked in [`launch-ops-checklist.md`](launch-ops-checklist.md) (Railway CI vars, webhook, deploy health, e2e, 20-user pilot, `factory-implement` automation).

---

## Recently shipped

Full history in [`tasks-archive.md`](tasks-archive.md). Latest: T-213 / T-214 / T-215 (PR #28), link-qr v1 (PR #36).

---

## Suggested next product decisions

1. **T-302** event duplication (Human summary approve) — duplicate from admin archive detail.
2. Whether **T-301** ownership/edit is next Iteration 3 priority (split required).
3. Do **not** enqueue T-202 product work — deferred to concierge (ADR-016) until clear demand.
