"""Regression tests for admin bot callback routing."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from app.bot.states import AdminStates


def test_edit_confirm_does_not_match_edit_start_pattern():
    assert "admin:edit:confirm".startswith("admin:edit:")
    import re

    assert re.match(r"^admin:edit:\d+$", "admin:edit:confirm") is None
    assert re.match(r"^admin:edit:\d+$", "admin:edit:42") is not None


def test_edit_confirm_handler_matches_without_fsm_state():
    router = Router()
    matched: list[str] = []

    @router.callback_query(F.data.regexp(r"^admin:edit:\d+$"))
    async def admin_edit_start(callback: CallbackQuery, state: FSMContext):
        matched.append("edit_start")
        await callback.answer()

    @router.callback_query(F.data == "admin:edit:confirm")
    async def edit_confirm(callback: CallbackQuery, state: FSMContext):
        matched.append("edit_confirm")
        await callback.answer()

    async def run() -> None:
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        dp.include_router(router)
        bot = Bot(token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz")

        user = User(id=1, is_bot=False, first_name="A")
        chat = Chat(id=1, type="private")
        msg = Message(message_id=1, date=0, chat=chat)
        cb = CallbackQuery(
            id="1",
            from_user=user,
            chat_instance="x",
            data="admin:edit:confirm",
            message=msg,
        )
        key = StorageKey(bot_id=bot.id, chat_id=chat.id, user_id=user.id)
        ctx = FSMContext(storage=storage, key=key)
        await ctx.set_state(AdminStates.EDIT_IMAGE)

        with patch.object(CallbackQuery, "answer", new_callable=AsyncMock):
            await dp.feed_update(bot, Update(update_id=1, callback_query=cb))

        assert matched == ["edit_confirm"]

    asyncio.run(run())
