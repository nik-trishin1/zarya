from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


def apply_schema_updates(connection: Connection) -> None:
    inspector = inspect(connection)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "bot_blocked_at" in columns:
        return

    if connection.dialect.name == "postgresql":
        ddl = "ALTER TABLE users ADD COLUMN bot_blocked_at TIMESTAMPTZ"
    else:
        ddl = "ALTER TABLE users ADD COLUMN bot_blocked_at DATETIME"

    connection.execute(text(ddl))
