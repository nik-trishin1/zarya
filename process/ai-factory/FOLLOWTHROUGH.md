# Followthrough (portable)

Shipping is not the end of a change. If a **product** change claims a user-visible effect, record how you will check it, then come back and decide.

## When to use

- Use it for product changes that claim an effect: conversion, retention, fewer errors, faster flow, higher registrations.
- Skip it for pure docs/process changes, refactors, and bugfixes with no measurable claim.
- Open the row **before merge**. Fill the verdict after the check-by date.

## Where to store

Preferred home: Project store `docs/followthrough/<change-id>.md` (for example `/cursor/stores/<project>/docs/followthrough/T-NNN.md`).

- Open the row in that path **before merge**.
- Link the store path from the PR and the ticket.
- After check-by, fill the verdict in the **same** file.
- Prefer the store over burying the only copy in a closed PR body or in `tasks.md` (tasks track work; followthrough tracks post-ship claims).

## Template

Copy into the store file (and optionally summarize in the PR with a link).

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
- Record the verdict in the same store followthrough file, not only in chat.
