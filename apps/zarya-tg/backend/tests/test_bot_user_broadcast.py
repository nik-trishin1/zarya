from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.bot_user_broadcast import (
    build_bot_user_broadcast_preview,
    send_bot_user_broadcast,
    validate_broadcast_body,
)


def test_build_bot_user_broadcast_preview():
    preview = build_bot_user_broadcast_preview("Привет, друзья!", 5)
    assert "Получателей: 5" in preview
    assert "Привет, друзья!" in preview


def test_validate_broadcast_body_rejects_empty():
    assert validate_broadcast_body("   ") == "Сообщение не может быть пустым."


@pytest.mark.asyncio
async def test_send_bot_user_broadcast_delegates_to_delivery():
    user = MagicMock()
    user.telegram_id = 1001
    with patch(
        "app.services.bot_user_broadcast.send_configured_bot_broadcast",
        new_callable=AsyncMock,
        return_value=(2, 0, 0),
    ) as deliver:
        sent, blocked, failed = await send_bot_user_broadcast([user, user], "Тест")
    assert sent == 2
    assert blocked == 0
    assert failed == 0
    deliver.assert_awaited_once_with(
        [user, user],
        "Тест",
        context="bot_user_broadcast",
    )
