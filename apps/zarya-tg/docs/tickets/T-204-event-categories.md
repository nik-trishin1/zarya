# T-204 — Event categories and filters


## Human summary (review this first)

**Will do:**
- (After ADR) Add categories and filter chips on the home list

**Will not do:**
- Implement before category ADR exists

**Touched areas:** Event model, home header filters

**Risk:** Medium without ADR — not Ready

**Smoke check after merge:** Filter chip narrows the list

**Reviewer decision:** `[ ] Approved to implement` — needs ADR first

---

| Field | Value |
|-------|-------|
| ID | T-204 |
| Title | Add event categories with header filter chips |
| Status | `todo` |
| Spec / ADR | Needs ADR before factory enqueue (category enum + API) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Users can filter the event list by category when the catalog grows (~15+ events).

## Acceptance Criteria

- [ ] ADR defines categories: Развлечения, Путешествия, Образование, Встречи (store English keys in DB if needed; UI Russian)
- [ ] Event create/edit (bot admin) can set category
- [ ] Home header shows filter chips; default = all; selecting a chip filters the list client- or server-side
- [ ] Events without category appear under «Все» only
- [ ] Tests cover filter API or client filter helper
- [ ] Frontend lint + build pass

## Out of Scope

- Multi-select filters
- Geo filters
- Category icons beyond simple chip labels (no emoji requirement)

## Implementation Notes

- Write ADR first; then mark DoR and enqueue. Until ADR exists, treat as not Ready for Automation.
