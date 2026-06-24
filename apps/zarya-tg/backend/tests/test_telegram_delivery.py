from __future__ import annotations

from aiogram.exceptions import TelegramForbiddenError

from app.services.telegram_delivery import is_bot_blocked_error, is_user_unreachable_error


def test_is_bot_blocked_error_matches_telegram_message():
    exc = TelegramForbiddenError(method=None, message="Forbidden: bot was blocked by the user")  # type: ignore[arg-type]
    assert is_bot_blocked_error(exc) is True


def test_is_bot_blocked_error_rejects_other_forbidden():
    exc = TelegramForbiddenError(method=None, message="Forbidden: chat not found")  # type: ignore[arg-type]
    assert is_bot_blocked_error(exc) is False


def test_is_user_unreachable_includes_deactivated():
    exc = TelegramForbiddenError(method=None, message="Forbidden: user is deactivated")  # type: ignore[arg-type]
    assert is_user_unreachable_error(exc) is True
    assert is_bot_blocked_error(exc) is False
