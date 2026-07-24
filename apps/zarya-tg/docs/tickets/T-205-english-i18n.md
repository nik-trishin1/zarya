# T-205 — English localization


## Human summary (review this first)

**Will do:**
- (After ADR) Add English UI while keeping Russian default

**Will not do:**
- Full bot translation in the first slice unless ADR says so

**Touched areas:** Frontend strings, possibly API locale

**Risk:** Medium — string coverage gaps

**Smoke check after merge:** Default remains Russian; English toggles key screens

**Reviewer decision:** `[ ] Approved to implement` — needs ADR first

---

| Field | Value |
|-------|-------|
| ID | T-205 |
| Title | Add i18n layer with English locale |
| Status | `todo` |
| Spec / ADR | Needs ADR (library choice, key structure, bot message strategy) |
| App | `zarya-tg` |
| Estimate | L — split into frontend / backend / bot tickets after ADR |

## Goal

Support English UI while keeping Russian as default.

## Acceptance Criteria

- [ ] ADR chooses i18n approach (e.g. react-i18next + backend locale param)
- [ ] Russian remains default when locale missing
- [ ] Critical Mini App strings (home empty state, register/cancel, errors) exist in `en` and `ru`
- [ ] Bot messages strategy documented (ship or defer in ADR)
- [ ] Lint + build pass; no hardcoded English regressions for default ru users

## Out of Scope

- Full translation of every admin FSM string in the first PR (may be a follow-up ticket)
- Auto language detection beyond Telegram language_code if ADR defers it

## Implementation Notes

- Not factory-ready until ADR exists and this ticket is split to ≤1 PR each.
