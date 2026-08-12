# zarya — Task Backlog

> Refreshed 2026-08-12. Tickets: [`docs/tickets/`](tickets/). Process: [`process/ai-factory/`](../../../process/ai-factory/).

## Status Legend

`[ ]` Not started · `[~]` In progress · `[x]` Done · `[-]` Blocked / cancelled

**DoR** = Definition of Ready (`process/ai-factory/DEFINITION_OF_READY.md`): approved Human summary + linked ADR/spec + verifiable AC.

---

## Open backlog (review this)

Ordered for product triage — not a factory queue. Nothing below is factory-ready until DoR = yes.

### Needs Human summary approve (ADR exists)

| ID | Title | Blocker | Links |
|----|-------|---------|-------|
| **T-211** | Maybe RSVP («Подумаю») + delayed bot ping | Approve Human summary | [ticket](tickets/T-211-maybe-rsvp-delayed-ping.md) · [ADR-022](decisions/022-maybe-rsvp-delayed-ping.md) |
| **T-203** | Past events archive («Завершено») | Approve + thin UI notes in ticket | [ticket](tickets/T-203-past-events-archive.md) · [ADR-018](decisions/018-hide-past-events.md) |
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
| **T-202** | Propose your own event | ADR-016 | [ticket](tickets/T-202-propose-event.md) |
| **T-303** | Invite system | Invite ADR | [ticket](tickets/T-303-invite-system.md) |
| **T-304** | Public web version (zarya.org) | Web ADR | [ticket](tickets/T-304-web-version.md) |

### Cancelled

| ID | Title | Reason | Links |
|----|-------|--------|-------|
| **T-205** | English i18n | Russian-only (ADR-003) | [ticket](tickets/T-205-english-i18n.md) |

### Ops / launch (Phase 4 leftovers)

- [ ] Configure GitHub secrets/vars for Railway log scan (`RAILWAY_TOKEN`, `RAILWAY_SERVICE_NAMES`, …)
- [ ] End-to-end testing with real Telegram accounts
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Railway (static hosting)
- [ ] Configure Telegram bot webhook
- [ ] Invite initial 20 users and validate flows
- [ ] Fix bugs from user testing
- [ ] Operator: create Cursor Automation `factory-implement` (see `process/ai-factory/ORCHESTRATOR.md`)

---

## Shipped (Iteration 2+)

- [x] Event capacity limit — ADR-012
- [x] New event announcement broadcast — ADR-011
- [x] Admin broadcast to all bot users — ADR-017
- [x] 24h reminder to registered participants — ADR-013
- [x] Shareable deep-link per event — ADR-010
- [x] Hide past events from active UI — ADR-018
- [x] **T-207** Registration +1 (`party_size`) — [ticket](tickets/T-207-registration-plus-one.md) · ADR-019
- [x] **T-208** Access groups — [ticket](tickets/T-208-access-groups.md) · ADR-020
- [x] **T-209** Backend `is_featured` + bot create/edit — [ticket](tickets/T-209-is-featured-bot.md) · [S-209](specs/S-209-home-poster-slider.md) · ADR-021
- [x] **T-210** Home poster slider (frontend) — [ticket](tickets/T-210-home-poster-slider.md)

## Shipped (MVP Phases 0–3 + process)

- [x] Phase 0 — repo & docs (PRD, AGENTS, decisions seed)
- [x] Phase 1 — FastAPI backend, schema, Railway Docker, bot skeleton, CRUD, registrations, .ics, tests
- [x] Phase 2 — React Mini App (list, details, register, my registrations, calendar, design system)
- [x] Phase 3 — Admin bot (`/admin` create/edit/delete/list)
- [x] CI gates + Railway log scan wiring — T-FACTORY-001
- [x] Portable AI-Factory process — T-FACTORY-002 / S-FACTORY-001

---

## Suggested next product decisions

1. **Approve or revise T-211** Human summary (ADR-022 already locked) → then implement.
2. **T-203** archive UX approve vs leave past events hidden-only (ADR-018).
3. Whether **T-301** ownership/edit is next Iteration 3 priority (split required) vs more Iteration 2 ADRs (categories / analytics).
