# T-301 — Event ownership and in-app admin editing


## Human summary (review this first)

**Will do:**
- Add ownership/status on events and an in-app edit sheet for allowed users (per ADR-014)
- On cancel, notify registrants and admin

**Will not do:**
- Ship as one giant PR — must be split into child tickets before factory enqueue
- Notion-like CMS editing

**Touched areas:** Event model, Mini App details, bot supplementary flows

**Risk:** High as a single ticket — split required

**Smoke check after merge:** Editor sees pencil; unauthorized user does not; cancel notifies

**Reviewer decision:** `[ ] Approved to implement` — only after child tickets exist

---

| Field | Value |
|-------|-------|
| ID | T-301 |
| Title | Event ownership + in-app edit sheet |
| Status | `todo` |
| Spec / ADR | [ADR-014](../decisions/014-event-ownership-and-inline-editing.md) |
| App | `zarya-tg` |
| Estimate | L — **split before factory enqueue** into model, API, UI, bot parity tickets |

## Goal

Events have ownership/status; admins and initiators can edit in-app per the ADR permission matrix.

## Acceptance Criteria (epic-level — split required)

- [ ] `proposed_by_user_id` and `status` on Event per ADR-014
- [ ] API exposes `can_edit` consistently with permission matrix
- [ ] In-app edit sheet (pencil) when `can_edit: true`
- [ ] Cancellation broadcasts to registrants and DM to admin per ADR
- [ ] Bot FSM remains supplementary, not removed
- [ ] Tests for permissions and cancel side effects
- [ ] Frontend lint + build pass

## Out of Scope

- Full CMS / Notion-like editor
- Participant-visible editor for non-initiators

## Implementation Notes

- DoR for factory: create child tickets (T-301a model/API, T-301b Mini App sheet, T-301c cancel broadcast) each ≤1 PR.
- Do not enqueue this epic as a single Automation job.
