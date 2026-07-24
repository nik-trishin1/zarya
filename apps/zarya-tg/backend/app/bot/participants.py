from __future__ import annotations

from app.models.user import User


def format_participant_line(index: int, user: User, *, plus_one_index: int | None = None) -> str:
    name = (user.first_name or "Участник").strip()
    if plus_one_index is not None:
        return f"{index}. {name} + {plus_one_index}"
    if user.username:
        return f"{index}. {name} @{user.username}"
    return f"{index}. {name}"


def expand_participant_lines(users_with_party: list[tuple[User, int]]) -> list[str]:
    """Expand each registration into party_size numbered lines (ADR-019)."""
    lines: list[str] = []
    index = 1
    for user, party_size in users_with_party:
        size = max(int(party_size), 1)
        lines.append(format_participant_line(index, user))
        index += 1
        for extra in range(1, size):
            lines.append(format_participant_line(index, user, plus_one_index=extra))
            index += 1
    return lines


def format_participants_message(
    event_name: str,
    users: list[User] | list[tuple[User, int]],
) -> str:
    if not users:
        return f"Участники: {event_name}\n\nПока никто не зарегистрирован."

    # Backward-compatible: plain User list → party_size 1 each
    if users and not isinstance(users[0], tuple):
        parties = [(user, 1) for user in users]  # type: ignore[misc]
    else:
        parties = list(users)  # type: ignore[arg-type]

    lines = expand_participant_lines(parties)
    body = "\n".join(lines)
    return f"Участники: {event_name}\n\n{body}\n\nВсего: {len(lines)}"
