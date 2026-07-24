# T-302 — Event duplication


## Human summary (review this first)

**Will do:**
- Let admin copy an event as a template with empty/new date-time

**Will not do:**
- Copy registrations or build a full recurrence system

**Touched areas:** Admin create/edit flows

**Risk:** Low–medium; prefer after ownership/status fields if drafts are required

**Smoke check after merge:** Duplicate creates a new event; original unchanged

**Reviewer decision:** `[ ] Approved to implement`

---

| Field | Value |
|-------|-------|
| ID | T-302 |
| Title | Admin duplicates event as template |
| Status | `todo` |
| Spec / ADR | Related to ADR-014 / admin flows; may need thin ADR addendum |
| App | `zarya-tg` |
| Estimate | S |

## Goal

Admin can copy an existing event with all fields pre-filled except date/time.

## Acceptance Criteria

- [ ] Admin action (bot and/or in-app) creates a new event draft/copy from an existing event_id
- [ ] Copied fields: name, location, description, cover, capacity/category if present; date/time empty or requiring explicit set before publish
- [ ] Original event unchanged
- [ ] Backend test for duplicate service
- [ ] Russian confirmation copy in admin UI/bot

## Out of Scope

- Duplicating registrations
- Recurring event series

## Implementation Notes

- Prefer implementing after T-301 status/ownership fields exist if copy must set `draft`/`proposed_by`.
