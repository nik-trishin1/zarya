# T-212 — Almost-full nudge for maybe RSVPs


## Human summary (review this first)

**Will do:**
- When an event is nearly full, DM users still on «Подумаю» with a short nudge to confirm (e.g. «Места почти закончились — присоединяйся») and **«Буду» / «Не смогу»**

**Will not do:**
- Soft-hold seats for maybe
- Change capacity math

**Touched areas:** maybe ping / capacity hooks, bot copy

**Risk:** Low — additive notifications only

**Smoke check after merge:** Fill event to near capacity with maybe users present → they get the nudge once

**Reviewer decision:** `[ ] Approved to implement` · Reviewer: ____ · Date: ____

---

| Field | Value |
|-------|-------|
| ID | T-212 |
| Title | Almost-full nudge for maybe RSVPs |
| Status | `todo` |
| Spec / ADR | Follow-on to [ADR-022](../decisions/022-maybe-rsvp-delayed-ping.md) / [T-211](T-211-maybe-rsvp-delayed-ping.md); needs thin ADR addendum before factory |
| App | `zarya-tg` |
| Estimate | S |
| Priority | Low |

## Goal

Prompt undecided («Подумаю») users when remaining seats are low so they confirm or decline before the event fills.

## Acceptance Criteria

- [ ] Define threshold (e.g. ≤N seats left or ≤X% remaining) in ADR addendum
- [ ] At most one almost-full nudge per maybe registration
- [ ] Inline **«Буду»** / **«Не смогу»** reuse T-211 callbacks
- [ ] Capacity and ADR-013 behavior unchanged

## Out of Scope

- Waitlists / seat holds
- Changing T-211 cascade day offsets

## Implementation Notes

- Deferred from T-211 capacity corner-case discussion (2026-08-12)
- Not DoR until threshold + copy approved
