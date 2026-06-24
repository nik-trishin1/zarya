# ADR-014 — Event Ownership & In-App Admin Editing

**Status:** Proposed  
**Iteration:** 3  
**Date:** 2026-06-24

---

## Context

Currently, all event management (create, edit, delete) is handled exclusively through Telegram bot inline commands (`/admin` FSM flow). Two limitations have emerged:

1. **Admin UX friction** — editing an event requires navigating a multi-step bot conversation rather than tapping fields directly in the Mini App.
2. **No event ownership** — all events are owned by `admin`. When a participant proposes an event (planned for Iteration 2), they have no way to manage it after approval.

This ADR defines the data model changes, permission rules, and UI/UX requirements to introduce **event ownership** and **in-app editing** for both admin and event initiators.

---

## Decision

Introduce a lightweight ownership model using the existing `created_by_admin_id` field (renamed to `created_by_user_id`) and a new `proposed_by_user_id` field. No new roles table is created. Permissions are enforced at the API layer via simple field comparisons.

---

## Data Model Changes

### `events` table

| Field | Change | Notes |
|-------|--------|-------|
| `created_by_admin_id` | Rename → `created_by_user_id` | Already exists; references `users.user_id` |
| `proposed_by_user_id` | **Add** (nullable `BigInteger FK → users.user_id`) | Set when a participant submits a proposal (Iteration 2 flow); `NULL` for admin-created events |
| `status` | **Add** (`VARCHAR(20)`, default `'published'`) | Values: `draft` (pending approval), `published`, `cancelled` |

### Migration notes

- `created_by_admin_id` rename is backward-compatible via SQLAlchemy `mapped_column(name="created_by_admin_id")` alias until migration is applied.
- Add DB migration file: `alembic/versions/014_event_ownership.py`.

---

## Permission Matrix

| Action | Admin | Event Initiator (proposed_by) | Regular User |
|--------|-------|-------------------------------|--------------|
| View published event | ✅ | ✅ | ✅ |
| View draft event | ✅ | ✅ (own only) | ❌ |
| Edit name / description / date / time / location / cover | ✅ | ✅ (own only) | ❌ |
| Cancel event (`status → cancelled`) | ✅ | ✅ (own only, triggers admin notification) | ❌ |
| Delete event (hard delete) | ✅ | ❌ | ❌ |
| View participant list | ✅ | ❌ | ❌ |
| Broadcast to participants | ✅ | ❌ | ❌ |
| Approve / reject draft | ✅ | ❌ | ❌ |

**Permission check logic (API layer):**

```python
def can_edit_event(user: User, event: Event) -> bool:
    if user.telegram_id in get_settings().admin_ids:
        return True
    if event.proposed_by_user_id == user.user_id:
        return True
    return False
```

---

## API Changes

### Existing endpoints — extend

| Endpoint | Change |
|----------|--------|
| `GET /events` | Exclude `cancelled` events from public list; show with grey overlay if `is_past` |
| `GET /events/{id}` | Return `can_edit: bool` field based on permission check |
| `PUT /events/{id}` | Currently admin-only via bot; open to initiator with permission check |
| `DELETE /events/{id}` | Remain admin-only |

### New endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `PATCH /events/{id}/cancel` | Authenticated | Initiator or admin; sends cancellation broadcast to registrants |
| `GET /admin/events/drafts` | Admin only | List all draft events pending approval |
| `POST /admin/events/{id}/approve` | Admin only | Publish a draft event; triggers announcement |
| `POST /admin/events/{id}/reject` | Admin only | Delete draft; optionally notify proposer |

---

## Frontend (Mini App) Changes

### Event Details screen

Add an **edit button** (pencil icon `✏️`) in the top-right corner of the event details screen, visible only when `can_edit: true` is returned by the API.

Tapping the edit button opens an **inline edit sheet** (bottom sheet / modal) with the following editable fields:

| Field | Input type |
|-------|-----------|
| Name | Text input |
| Description | Textarea |
| Date | Date picker |
| Time | Time picker |
| Location | Text input |
| Cover image | File upload (reuse existing `CoverImage` component) |

The sheet has two actions: **Save** (PATCH `/events/{id}`) and **Cancel event** (PATCH `/events/{id}/cancel` with confirmation dialog).

**Cancel confirmation dialog:**
> "Вы уверены? Все зарегистрированные участники получат уведомление об отмене."
> [Отменить событие] [Назад]

### Home screen

Cancelled events: show with `opacity: 0.5` and a "Отменено" badge. Remove registration button. Keep visible for 24 hours after cancellation, then hide.

### Admin bot — supplement, not replace

The existing bot FSM flow (`/admin`) remains fully functional. In-app editing is an **additional** interface, not a replacement. Admin can use whichever is more convenient.

---

## Notifications

| Trigger | Recipients | Message |
|---------|-----------|---------|
| Initiator cancels event | Admin (via bot DM) | "⚠️ [Имя] отменил(а) событие «{name}» ({date})." |
| Initiator edits event | Admin (via bot DM) | "✏️ [Имя] изменил(а) событие «{name}»: {changed_fields}." |
| Admin approves draft | Initiator (via bot DM) | "✅ Ваше событие «{name}» одобрено и опубликовано!" |
| Admin rejects draft | Initiator (via bot DM) | "❌ Ваше событие «{name}» не было одобрено." |
| Event cancelled (any actor) | All registrants (broadcast) | "❌ Событие «{name}» ({date}) отменено." |

---

## Schemas — additions to `event.py`

```python
class EventUpdate(BaseModel):
    # existing fields remain
    status: Literal["published", "cancelled"] | None = None

class EventResponse(BaseModel):
    # existing fields remain
    status: str  # "published" | "cancelled" | "draft"
    can_edit: bool = False  # computed per-request
    proposed_by_first_name: str | None = None  # shown in admin view
```

---

## Out of Scope (Iteration 3)

- Multi-admin support
- Initiator can view participant list
- Initiator can broadcast to participants
- Waitlist logic
- Event duplication (separate backlog item)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Initiator cancels event without warning | Mandatory confirmation dialog + admin notification |
| Concurrent edits (admin + initiator simultaneously) | `updated_at` optimistic locking — return 409 if client `updated_at` < server `updated_at` |
| Accidental hard delete by admin in new UI | Keep delete only in bot FSM; in-app UI only has "cancel" |

---

## Open Questions

1. Should cancelled events be permanently hidden after 24h, or moved to an "Archive" section?
2. Should the initiator receive a notification when their event is edited by admin?
3. Is event duplication (copy as template) in scope for Iteration 3 or separate?
