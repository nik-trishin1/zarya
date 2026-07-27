# S-209 — Soft registration deadline reminder

## Human summary (review this first)

**In plain language, we will:**
- Let the admin optionally set a **registration deadline date** on an event (whole day in Moscow time; empty = no deadline).
- On the **calendar day before** that date, automatically message people in the event’s audience who have **not** registered yet: public events → all bot users; group events → that group’s members.
- Show the deadline in the Mini App as information only.
- Keep registration and cancellation working even after the deadline date (soft nudge, not a lock).

**We will not:**
- Block new registrations or cancellations after the deadline.
- Add waitlists, multiple reminder cadences, or deadline catch-up on the deadline day itself.
- Change who can see group vs public events (still ADR-020).

**User-visible outcome:**
- Admin can set or clear a deadline when creating/editing an event.
- Eligible non-registrants get one Telegram DM the day before, with a deep link to register.
- Event details show «Регистрация до … включительно» when a deadline is set.

**Main risks / open questions already decided:**
- Soft only (product). Date-only end of MSK day (product).
- Reminder day = exactly one Moscow calendar day before the deadline (fits existing 08:00–22:00 scheduler; avoids 23:59 window).
- Independent from the existing “event tomorrow” reminder to people already registered.

**How we will know it worked (smoke):**
- Automated: pytest for recipient filtering, reminder day window, idempotency; frontend lint/build with deadline field displayed.
- Manual: create event with deadline tomorrow → eligible users get DM; registered users do not; after deadline date, register button still works.

**Reviewer decision:** `[x] Approved for ticket split` · Reviewer: product (chat) · Date: 2026-07-27

---

## Metadata

| Field | Value |
|-------|-------|
| Spec ID | S-209 |
| Title | Soft registration deadline + day-before reminder |
| Status | `approved` |
| Related ADR / PRD | [ADR-021](../decisions/021-registration-deadline-reminder.md), ADR-013, ADR-020 |
| Owner | product |

## Problem

Organizers sometimes want a shared “please decide by …” date and a nudge to people who have not RSVP’d, without locking the form after that date.

## Goals

- Optional per-event deadline date (MSK end-of-day semantics for copy).
- One automated reminder to non-registrants in the event audience, day before.
- Transparent UI display; no hard gate.

## Non-goals

- Hard registration cutoff.
- Email/SMS or in-app push outside Telegram DMs.
- Reminding already-registered users about the deadline.
- Editing audience after create (unchanged from ADR-020).

## Proposed behavior

### Data / API

- Columns: `registration_deadline_date`, `registration_deadline_reminder_sent_at` (see ADR-021).
- Event JSON: `registration_deadline_date`, optional `is_registration_deadline_passed`.
- Register/cancel endpoints: no new 4xx for deadline.

### UI / bot copy (user-facing language)

- Admin prompt: «Дедлайн регистрации (ДД.ММ.ГГГГ) или „Без дедлайна“».
- Reminder DM: see ADR-021 template («Скоро закрывается регистрация!»).
- Mini App: «Регистрация до {date} включительно»; if passed, informational line only.

### Errors and edge cases

- Invalid date / deadline after event date / deadline before today on save → reject with clear Russian bot error.
- Empty recipient list → still mark reminder sent.
- Process down on reminder day → no v1 catch-up (ADR-021).

## Acceptance criteria (spec-level)

- [ ] Optional deadline on create and edit; `NULL` means no reminder job.
- [ ] Day-before MSK reminder once to audience minus active registrants.
- [ ] Group vs public recipient scoping matches announce audience.
- [ ] Soft: post-deadline register/cancel still succeed (unless past/full/other existing rules).
- [ ] Mini App shows deadline when set; does not block on deadline alone.
- [ ] Tests cover window, idempotency, recipient exclusion of registrants.

## Rollout / migration

- Additive nullable columns via existing `schema_updates` pattern; existing events stay without deadline.

## Open questions

> None for v1 — product chose soft + date-only.
