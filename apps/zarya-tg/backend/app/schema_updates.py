from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


def _add_column_if_missing(
    connection: Connection,
    table: str,
    column: str,
    ddl_postgresql: str,
    ddl_sqlite: str,
) -> None:
    inspector = inspect(connection)
    if table not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns(table)}
    if column in columns:
        return
    ddl = ddl_postgresql if connection.dialect.name == "postgresql" else ddl_sqlite
    connection.execute(text(ddl))


def apply_schema_updates(connection: Connection) -> None:
    _add_column_if_missing(
        connection,
        "users",
        "bot_blocked_at",
        "ALTER TABLE users ADD COLUMN bot_blocked_at TIMESTAMPTZ",
        "ALTER TABLE users ADD COLUMN bot_blocked_at DATETIME",
    )
    _add_column_if_missing(
        connection,
        "events",
        "max_participants",
        "ALTER TABLE events ADD COLUMN max_participants INTEGER",
        "ALTER TABLE events ADD COLUMN max_participants INTEGER",
    )
    _add_column_if_missing(
        connection,
        "events",
        "reminder_sent_at",
        "ALTER TABLE events ADD COLUMN reminder_sent_at TIMESTAMPTZ",
        "ALTER TABLE events ADD COLUMN reminder_sent_at DATETIME",
    )
    _add_column_if_missing(
        connection,
        "registrations",
        "party_size",
        "ALTER TABLE registrations ADD COLUMN party_size INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE registrations ADD COLUMN party_size INTEGER NOT NULL DEFAULT 1",
    )
    _seed_event_capacity_limits(connection)


def _seed_event_capacity_limits(connection: Connection) -> None:
    inspector = inspect(connection)
    if "events" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("events")}
    if "max_participants" not in columns:
        return
    connection.execute(
        text("UPDATE events SET max_participants = 20 WHERE event_id IN (4, 5)")
    )
