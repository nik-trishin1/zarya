# ADR-020: Access groups for closed events

**Date:** 2026-07-24
**Status:** Accepted

## Context

The community needs closed events visible only to a named circle (starting with **Core**), plus group-scoped admin broadcasts. PRD historically described tier names (`friends` / `circle` / `core`) and access codes (T-201 / future ADR). Operators also need a simple way to put known Telegram users into a group via the database before any UI exists.

Requirements for this iteration:

1. Named groups with many-to-many membership (a user may belong to several groups later; ops may use one for now).
2. Each event has one audience: all bot users, or one group.
3. Group events: no +1, no share button (avoids deep-link leaks).
4. New-event announcements for a group go **only** to that group's members.
5. Admins see all events in the Mini App and admin bot without needing membership.
6. Access codes stay a **future** join path into the same membership table — not a parallel ACL.

`events.tier` (default `"friends"`) was never used for filtering and must not become a second source of truth.

## Decision

### Schema

- Table `access_groups`: `group_id`, unique `slug`, `name`, `created_at`.
- Table `group_memberships`: `membership_id`, `user_id`, `group_id`, `joined_at`, `source` (`admin` now; later `access_code`), unique `(user_id, group_id)`.
- Column `events.audience_group_id` (nullable FK → `access_groups`). `NULL` = public («Все участники»).
- Seed group `slug=core`, `name=Core`.
- Configured Core roster `CORE_SEED_USER_IDS` is applied at app startup (`seed_core_roster`); newly added members receive the welcome DM once (idempotent on restart).
- Ignore / deprecate `events.tier` for ACL; do not write or read it for visibility.

### Visibility and registration

| Action | Public (`audience_group_id IS NULL`) | Group event |
|--------|--------------------------------------|-------------|
| List / detail | All authenticated users | Members **or** admins (`ADMIN_TELEGRAM_IDS`) |
| Register | As today; +1 allowed | Member or admin; `party_size` must be `1` |
| PATCH +1 | As today | Rejected |
| Share UI | Shown | Hidden (`allows_sharing=false`) |
| New-event notify | All bot users | **Group members only** |
| Reminders / participant broadcast | Active registrants | Unchanged |

Non-member, non-admin detail → **404**. API exposes `audience_group_id`, `allows_plus_one`, `allows_sharing` (derived: public ⇒ both true).

Admin bypass is by Telegram admin IDs, not by auto-enrolling admins into every group (so group announce recipient lists stay accurate).

### Admin bot

- Create-event FSM: choose audience («Все участники» or a group) before confirm.
- Confirm shows audience label and recipient count for that audience.
- Notify button labels distinguish all vs group; delivery uses the scoped recipient list.
- Menu: «📢 Написать группе» → pick group → text → confirm → send only to members.
- Manage list shows audience label; admins see all events.

### Membership ops (v1)

- Service `add_user_to_group(..., notify=True)` is idempotent; on first join with `notify=True`, send:
  `Привет! Теперь тебе доступны события группы *{name}*. До встречи!` (Markdown).
- No Mini App UI for membership in this iteration. Bulk Core roster after the operator's list is a follow-up ops step.

### Access codes (deferred)

Codes will redeem into `group_memberships` with `source=access_code`. T-201 remains blocked until a codes-specific ADR extends this model. Do not invent a separate access table that duplicates group ACL.

## Alternatives considered

**Reuse `events.tier` string.** Rejected — not relational, awkward for multi-group membership and named groups beyond a fixed enum.

**Auto-add admins to all groups.** Rejected — would inflate announce audiences and mix ops identity with membership.

**Keep share + deep links with 404 for outsiders.** Rejected — product chose to hide share on group events to avoid the corner case entirely.

## Consequences

- Public MVP flows (list, +1, share, all-user announce) stay unchanged when `audience_group_id` is null.
- Creating a Core event with notify after seed of `user_id=1` only messages Core members (initially that one user if no further roster).
- Agent / CI smoke must not run production «notify all» against the live bot; prefer unit tests and scoped group notify for manual post-release checks.
- Future access-code UI plugs into the same membership rows.
