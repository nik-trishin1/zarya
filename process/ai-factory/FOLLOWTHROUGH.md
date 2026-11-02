# Followthrough (portable)

Shipping is not the end of a change. If a **product** change claims a user-visible effect, record how you will check it, then come back and decide.

## When to use

- Use it for product changes that claim an effect: conversion, retention, fewer errors, faster flow, higher registrations.
- Skip it for pure docs/process changes, refactors, and bugfixes with no measurable claim.
- Open the row in the PR (or a doc linked from the ticket) **before merge**. Fill the verdict after the check-by date.

## Template

Copy into the PR body or a linked doc.

| Field | Value |
|-------|-------|
| Change ID | `T-NNN` / PR link |
| Baseline metric | Current value and where it was read (date, source) |
| Expected effect | Direction and size, e.g. "registrations per event +10%" |
| Check-by date | YYYY-MM-DD |
| How to measure | Exact query, dashboard, or log line; who runs it |
| Verdict | `keep` / `tweak` / `rollback` (fill after check) |
| Owner | Human who decides the verdict |

## Rules

- No baseline, no claim: if you cannot read a baseline, write "unknown" and say how you will approximate it.
- Verdicts: `keep` = effect seen or no harm; `tweak` = partial effect, open a follow-up ticket; `rollback` = no effect or harm, revert or open a revert ticket.
- A human owns the verdict. An agent may gather the numbers but does not sign off.
- Do not add tracking, analytics, or notifications to measure a change without a spec/ADR (out of MVP scope for `zarya-tg`). Prefer data you already have: DB counts, Railway logs, manual checks.
- Record the verdict next to the change (PR comment or the doc), not only in chat.
