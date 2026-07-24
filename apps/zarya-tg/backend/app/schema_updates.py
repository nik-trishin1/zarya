from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


CORE_GROUP_SLUG = "core"
CORE_GROUP_NAME = "Core"
OPERATOR_SEED_USER_ID = 1


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
    _add_column_if_missing(
        connection,
        "events",
        "audience_group_id",
        "ALTER TABLE events ADD COLUMN audience_group_id INTEGER",
        "ALTER TABLE events ADD COLUMN audience_group_id INTEGER",
    )
    _seed_event_capacity_limits(connection)
    _seed_core_access_group(connection)


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


def _seed_core_access_group(connection: Connection) -> None:
    """Ensure Core group exists; optionally silent-membership for users.user_id=1."""
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if "access_groups" not in tables:
        return

    existing = connection.execute(
        text("SELECT group_id FROM access_groups WHERE slug = :slug"),
        {"slug": CORE_GROUP_SLUG},
    ).fetchone()
    if existing is None:
        connection.execute(
            text("INSERT INTO access_groups (slug, name) VALUES (:slug, :name)"),
            {"slug": CORE_GROUP_SLUG, "name": CORE_GROUP_NAME},
        )
        existing = connection.execute(
            text("SELECT group_id FROM access_groups WHERE slug = :slug"),
            {"slug": CORE_GROUP_SLUG},
        ).fetchone()

    if existing is None or "group_memberships" not in tables or "users" not in tables:
        return

    group_id = int(existing[0])
    user_row = connection.execute(
        text("SELECT user_id FROM users WHERE user_id = :user_id"),
        {"user_id": OPERATOR_SEED_USER_ID},
    ).fetchone()
    if user_row is None:
        return

    membership = connection.execute(
        text(
            "SELECT membership_id FROM group_memberships "
            "WHERE user_id = :user_id AND group_id = :group_id"
        ),
        {"user_id": OPERATOR_SEED_USER_ID, "group_id": group_id},
    ).fetchone()
    if membership is not None:
        return

    # Silent seed — no Telegram welcome (ADR-020 / operator post-release test).
    connection.execute(
        text(
            "INSERT INTO group_memberships (user_id, group_id, source) "
            "VALUES (:user_id, :group_id, :source)"
        ),
        {
            "user_id": OPERATOR_SEED_USER_ID,
            "group_id": group_id,
            "source": "admin",
        },
    )
