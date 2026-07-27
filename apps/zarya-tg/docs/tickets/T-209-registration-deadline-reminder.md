# T-209 — Soft registration deadline reminder


## Human summary (review this first)

**Will do:**
- Add optional `registration_deadline_date` on events (end of that day MSK for messaging/copy; empty = none)
- Admin create + edit: set / change / clear deadline
- Day before deadline (MSK), DM audience members who are not actively registered (all users vs group — same as announce)
- Show deadline in Mini App; **do not** block register/cancel when the date has passed
- Idempotent `registration_deadline_reminder_sent_at` in the existing hourly scheduler

**Will not do:**
- Hard close of registration after the deadline
- Catch-up reminder on the deadline day
- Changing ADR-013 event-start reminders or audience ACL rules

**Touched areas:** event schema/API, admin bot create/edit FSM, reminder scheduler, Mini App event details

**Risk:** Medium — wrong recipient list could spam non-audience users; must reuse `get_announcement_recipients` and subtract active registrants

**Smoke check after merge:**
- Automated: pytest deadline window + recipient filter + soft register after date; frontend lint/build
- Manual: event with deadline = tomorrow → only non-registered audience gets DM; register still works after deadline date

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-07-27

---

| Field | Value |
|-------|-------|
| ID | T-209 |
| Title | Soft registration deadline + day-before reminder |
| Status | `todo` |
| Spec / ADR | [S-209](../specs/S-209-registration-deadline-reminder.md), [ADR-021](../decisions/021-registration-deadline-reminder.md) |
| App | `zarya-tg` |
| Estimate | M |

## Goal

Give organizers an optional soft registration deadline with one automatic nudge to people who still have not registered.

## Acceptance Criteria

- [ ] Schema: `registration_deadline_date`, `registration_deadline_reminder_sent_at`; exposed on event API
- [ ] Admin create FSM optional deadline step; edit can set/clear; validate ≥ today (MSK) and ≤ event date
- [ ] Scheduler (08:00–22:00 MSK): when `today + 1 day == deadline`, send once to announcement audience minus active registrants; deep link; mark sent even if zero recipients
- [ ] Does not interfere with ADR-013 `reminder_sent_at` flow
- [ ] Mini App shows deadline copy; registration not blocked solely because deadline passed
- [ ] Backend tests for window, idempotency, recipient exclusion; frontend lint/build pass

## Out of Scope

- Hard registration cutoff
- Deadline-day catch-up send
- Waitlist / capacity interaction changes beyond existing full/past rules
- Membership admin UI

## Implementation Notes

- Prefer extending `event_reminders.py` (or a sibling module called from the same `run.py` loop) rather than a second process
- Reuse `get_announcement_recipients`, `deliver_bot_message`, deep-link helpers from announce flow
- Reminder day rule is calendar-based (not 23–25h vs 23:59) — see ADR-021
- Defaults: no deadline on existing events; miss reminder if created after 22:00 on the day before deadline

## Verification

1. [ ] `PYTHONPATH=. pytest -q` in backend (deadline reminder + soft register cases)
2. [ ] `npm run lint && npm run build` in frontend
3. [ ] CI green
4. [ ] Review pass against AC (`process/ai-factory/REVIEW_PASS.md`)

## Handoff (when done)

- PR URL:
- Defaults chosen:
- Residual risks:
