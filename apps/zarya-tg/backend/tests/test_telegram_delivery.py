from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.telegram_delivery import DeliveryOutcome, deliver_bot_message, deliver_bot_messages_to_users


def _user(telegram_id: int = 1001, user_id: int = 1):
    user = MagicMock()
    user.telegram_id = telegram_id
    user.user_id = user_id
    user.bot_blocked_at = None
    return user


@pytest.mark.asyncio
async def test_deliver_bot_messages_to_users_counts_sent():
    bot = MagicMock()
    bot.send_message = AsyncMock()

    sent, blocked, failed = await deliver_bot_messages_to_users(
        bot,
        [_user(1001), _user(1002, user_id=2)],
        "Привет!",
        context="test_broadcast",
    )

    assert sent == 2
    assert blocked == 0
    assert failed == 0
    assert bot.send_message.await_count == 2


@pytest.mark.asyncio
async def test_deliver_bot_message_without_db_session_still_sends():
    bot = MagicMock()
    bot.send_message = AsyncMock()

    outcome = await deliver_bot_message(
        bot,
        None,
        1001,
        "Привет!",
        context="test_single",
    )

    assert outcome == DeliveryOutcome.SENT
    bot.send_message.assert_awaited_once()
