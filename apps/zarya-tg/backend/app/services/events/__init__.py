"""Event domain service — queries, mutations, and attendance serialization.

Public import path stays `app.services.events` (package replaces the former module).
"""

from app.services.events.mutations import (
    approve_registration,
    cancel_registration,
    clear_maybe_registration,
    create_event,
    delete_event,
    mark_maybe,
    register_user,
    reject_registration,
    update_event,
    update_party_size,
)
from app.services.events.queries import (
    _seat_count_for_event,
    get_all_events_admin,
    get_event_by_id,
    get_event_detail,
    get_event_maybe_users,
    get_event_pending_users,
    get_event_registered_users,
    get_event_registration_parties,
    get_past_events_admin,
    get_past_registered_events,
    get_upcoming_events,
)
from app.services.events.serialization import (
    EventAttendance,
    is_event_full,
    is_event_past,
    validate_party_size,
)

__all__ = [
    "EventAttendance",
    "_seat_count_for_event",
    "approve_registration",
    "cancel_registration",
    "clear_maybe_registration",
    "create_event",
    "delete_event",
    "get_all_events_admin",
    "get_event_by_id",
    "get_event_detail",
    "get_event_maybe_users",
    "get_event_pending_users",
    "get_event_registered_users",
    "get_event_registration_parties",
    "get_past_events_admin",
    "get_past_registered_events",
    "get_upcoming_events",
    "is_event_full",
    "is_event_past",
    "mark_maybe",
    "register_user",
    "reject_registration",
    "update_event",
    "update_party_size",
    "validate_party_size",
]
