# ADR-016: Defer user event proposals (concierge)

**Date:** 2026-09-16  
**Status:** Accepted  
**Ticket:** [T-202](../tickets/T-202-propose-event.md)

## Context

**Participant Core Job:** «I want to propose a meetup idea to the community so organizers can see it and optionally run it — without becoming an admin.»

**Admin Core Job:** «I want to take ideas from people without chaotic feed noise or accidental broadcasts.»

MVP event creation remains admin-only via the Telegram bot FSM (`/admin`). Ticket **T-202** asked for a product path (Mini App proposal form, draft entities, approve/reject pipeline). ADR number **016** was reserved for that decision and left empty while adjacent work (ADR-014 / T-301 ownership + in-app edit) stayed separate.

Product owner decision (2026-09-16): participants already know who the admin is and can message him directly. Building a propose/approve product is not justified yet.

## Decision

**Defer the product path.** Keep **option A (concierge)** for now:

- Participants propose ideas by messaging the admin in Telegram.
- Admin creates events with the existing create FSM when an idea is worth running.
- Do **not** build a Mini App proposal form, draft `Event` / proposal entities, or an approve/reject pipeline.

Revisit only if there is **clear demand** for “create my own events” (explicit volume or repeated requests that make manual concierge painful).

## Non-goals (for now)

- Option **B** — thin Mini App / bot form that DMs the admin without draft entities
- Option **C** — full draft → approve/reject → publish product pipeline
- Mixing this ticket into **ADR-014** / **T-301** (ownership + in-app editing remain a separate track)

## Relationship to other work

| Item | Relationship |
|------|----------------|
| **T-202** | Product implementation cancelled / deferred until demand; status tracks this ADR |
| **ADR-014** / **T-301** | Separate — ownership and in-app edit; do not silently absorb propose UX |
| **ADR-011** | Unchanged — announcements only when admin publishes via existing create flow |
| **ADR-025** | Unrelated — registration approval is not event-proposal moderation |

## Alternatives considered

**B — form → admin DM (no draft entity).** Useful probe if we need a visible “Propose” entry and structured ideas without a state machine. Deferred: unnecessary while concierge works and demand is unclear.

**C — draft → approve/reject pipeline.** Matches the original T-202 epic. Rejected for now: high build cost, overlaps ADR-014 fields, risks MVP scope creep before the Job is validated.

## Consequences

- No factory enqueue of T-202 product work until a future ADR revisits A → B/C.
- Admin load stays manual; acceptable while proposal volume is low.
- ADR-016 fills the numbering gap and unblocks backlog clarity (T-202 is no longer “blocked on missing ADR”).
