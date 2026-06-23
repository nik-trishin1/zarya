from __future__ import annotations

from app.models.user import User


def format_participant_line(index: int, user: User) -> str:
    name = (user.first_name or "Участник").strip()
    if user.username:
        return f"{index}. {name} @{user.username}"
    return f"{index}. {name}"


def format_participants_message(event_name: str, users: list[User]) -> str:
    if not users:
        return f"Участники: {event_name}\n\nПока никто не зарегистрирован."

    lines = [format_participant_line(index, user) for index, user in enumerate(users, start=1)]
    body = "\n".join(lines)
    return f"Участники: {event_name}\n\n{body}\n\nВсего: {len(users)}"
