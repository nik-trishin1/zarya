# T-205 — English localization


## Human summary (review this first)

**Will do:**
- Nothing — ticket cancelled

**Will not do:**
- English UI, i18n layer, or bot translation

**Touched areas:** Docs only (cancellation)

**Risk:** None

**Smoke check after merge:** N/A

**Reviewer decision:** Cancelled by product owner — Russian remains the only supported language

---

| Field | Value |
|-------|-------|
| ID | T-205 |
| Title | Add i18n layer with English locale |
| Status | `cancelled` |
| Spec / ADR | Superseded by standing Russian-only decision (ADR-003); no English ADR |
| App | `zarya-tg` |
| Estimate | — |

## Goal

~~Support English UI while keeping Russian as default.~~

**Cancelled (2026-08-05):** Product stays Russian-only. Do not implement English localization or i18n infrastructure unless a new ADR reopens the topic.

## Acceptance Criteria

- [x] Ticket cancelled; backlog and language ADR updated to Russian-only
- [ ] ~~ADR chooses i18n approach~~
- [ ] ~~Critical Mini App strings exist in `en` and `ru`~~

## Out of Scope

- All English / multi-locale work (entire ticket)

## Implementation Notes

- Cancelled intentionally; leave hardcoded Russian UI strings as-is (ADR-003).
