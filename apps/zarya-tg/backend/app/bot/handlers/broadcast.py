from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .common import _finish_admin_callback, is_admin
from app.bot.keyboards import (
    admin_menu_keyboard,
    back_to_event_keyboard,
    back_to_menu_keyboard,
    broadcast_all_confirm_keyboard,
    broadcast_confirm_keyboard,
    broadcast_group_confirm_keyboard,
    group_pick_keyboard,
)
from app.bot.states import AdminStates
from app.database import async_session
from app.services.access_groups import get_announcement_recipients, get_group_by_id, list_access_groups
from app.services.bot_user_broadcast import (
    build_bot_user_broadcast_preview,
    send_bot_user_broadcast,
)
from app.services.events import get_event_by_id, get_event_registered_users, is_event_past
from app.services.participant_broadcast import (
    build_broadcast_preview,
    send_participant_broadcast,
    validate_broadcast_body,
)
from app.services.users import get_all_users

router = Router()


@router.callback_query(F.data == "admin:broadcast:confirm")
async def admin_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    event_id = data.get("event_id")
    body = data.get("broadcast_text")
    if event_id is None or not body:
        await callback.answer("Сессия рассылки истекла", show_alert=True)
        return

    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        if is_event_past(event):
            await callback.answer("Нельзя рассылать по завершённым событиям", show_alert=True)
            return
        users = await get_event_registered_users(db, event_id)

    if not users:
        await callback.answer("Нет зарегистрированных участников", show_alert=True)
        return

    sent, blocked, failed = await send_participant_broadcast(users, event, body)

    await state.set_state(AdminStates.MANAGE_DETAIL)
    await state.update_data(event_id=event_id, edit_mode=False)
    result = f"Сообщение отправлено: {sent} из {len(users)}."
    if blocked:
        result += f" Заблокировали бота: {blocked}."
    if failed:
        result += " Есть недоставленные сообщения (см. логи сервера)."
    await _finish_admin_callback(callback, result, reply_markup=back_to_event_keyboard(event_id))


@router.callback_query(F.data.regexp(r"^admin:broadcast:\d+$"))
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        if is_event_past(event):
            await callback.answer("Нельзя рассылать по завершённым событиям", show_alert=True)
            return
        users = await get_event_registered_users(db, event_id)

    if not users:
        await callback.answer("Нет зарегистрированных участников", show_alert=True)
        return

    await state.set_state(AdminStates.BROADCAST_MESSAGE)
    await state.update_data(event_id=event_id, edit_mode=False)
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Введите текст сообщения для участников события «{event.name}».\n"
        f"Получателей: {len(users)}",
        reply_markup=back_to_event_keyboard(event_id),
    )
    await callback.answer()


@router.message(AdminStates.BROADCAST_MESSAGE)
async def admin_broadcast_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    error = validate_broadcast_body(message.text or "")
    if error:
        await message.answer(error)
        return

    data = await state.get_data()
    event_id = data.get("event_id")
    if event_id is None:
        await message.answer("Сессия рассылки истекла. Откройте событие и начните снова.")
        return

    body = (message.text or "").strip()
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await message.answer("Событие не найдено")
            return
        users = await get_event_registered_users(db, event_id)

    if not users:
        await message.answer("Нет зарегистрированных участников")
        return

    await state.update_data(broadcast_text=body)
    await state.set_state(AdminStates.BROADCAST_CONFIRM)
    preview = build_broadcast_preview(event, body, len(users))
    await message.answer(preview, reply_markup=broadcast_confirm_keyboard(event_id))


# --- Broadcast to all bot users ---

@router.callback_query(F.data == "admin:broadcast_all")
async def admin_broadcast_all_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as db:
        users = await get_all_users(db)

    if not users:
        await callback.answer("В боте пока нет пользователей", show_alert=True)
        return

    await state.set_state(AdminStates.ALL_BROADCAST_MESSAGE)
    await state.update_data(broadcast_scope="all", edit_mode=False)
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Введите текст сообщения для всех пользователей бота.\n"
        f"Получателей: {len(users)}",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.ALL_BROADCAST_MESSAGE)
async def admin_broadcast_all_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    error = validate_broadcast_body(message.text or "")
    if error:
        await message.answer(error)
        return

    body = (message.text or "").strip()
    async with async_session() as db:
        users = await get_all_users(db)

    if not users:
        await message.answer("В боте пока нет пользователей")
        await state.set_state(AdminStates.MENU)
        return

    await state.update_data(broadcast_text=body, broadcast_scope="all")
    await state.set_state(AdminStates.ALL_BROADCAST_CONFIRM)
    preview = build_bot_user_broadcast_preview(body, len(users))
    await message.answer(preview, reply_markup=broadcast_all_confirm_keyboard())


@router.callback_query(F.data == "admin:broadcast_all:confirm")
async def admin_broadcast_all_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    body = data.get("broadcast_text")
    if not body:
        await callback.answer("Сессия рассылки истекла", show_alert=True)
        return

    async with async_session() as db:
        users = await get_all_users(db)

    if not users:
        await callback.answer("В боте пока нет пользователей", show_alert=True)
        return

    sent, blocked, failed = await send_bot_user_broadcast(users, body)

    await state.set_state(AdminStates.MENU)
    await state.update_data(edit_mode=False)
    result = f"Сообщение отправлено: {sent} из {len(users)}."
    if blocked:
        result += f" Заблокировали бота: {blocked}."
    if failed:
        result += " Есть недоставленные сообщения (см. логи сервера)."
    await _finish_admin_callback(callback, result, reply_markup=admin_menu_keyboard())


# --- Broadcast to access group ---

@router.callback_query(F.data == "admin:broadcast_group")
async def admin_broadcast_group_pick(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as db:
        groups = await list_access_groups(db)

    if not groups:
        await callback.answer("Пока нет групп доступа", show_alert=True)
        return

    await state.set_state(AdminStates.GROUP_BROADCAST_PICK)
    await callback.message.edit_text(
        "Выберите группу для рассылки:",
        reply_markup=group_pick_keyboard(groups),
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^admin:broadcast_group:\d+$"))
async def admin_broadcast_group_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    group_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        group = await get_group_by_id(db, group_id)
        if group is None:
            await callback.answer("Группа не найдена", show_alert=True)
            return
        users = await get_announcement_recipients(db, group_id)

    if not users:
        await callback.answer("В группе пока нет участников", show_alert=True)
        return

    await state.set_state(AdminStates.GROUP_BROADCAST_MESSAGE)
    await state.update_data(
        broadcast_group_id=group_id,
        broadcast_group_name=group.name,
        edit_mode=False,
    )
    await callback.message.edit_text(
        f"Введите текст сообщения для группы «{group.name}».\n"
        f"Получателей: {len(users)}",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.GROUP_BROADCAST_MESSAGE)
async def admin_broadcast_group_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    error = validate_broadcast_body(message.text or "")
    if error:
        await message.answer(error)
        return

    data = await state.get_data()
    group_id = data.get("broadcast_group_id")
    group_name = data.get("broadcast_group_name") or "группа"
    if group_id is None:
        await message.answer("Сессия рассылки истекла. Начните снова из меню.")
        return

    body = (message.text or "").strip()
    async with async_session() as db:
        users = await get_announcement_recipients(db, group_id)

    if not users:
        await message.answer("В группе пока нет участников")
        await state.set_state(AdminStates.MENU)
        return

    await state.update_data(broadcast_text=body)
    await state.set_state(AdminStates.GROUP_BROADCAST_CONFIRM)
    preview = (
        f"Проверьте сообщение для группы «{group_name}». "
        f"Получателей: {len(users)}\n\n———\n{body}\n———"
    )
    await message.answer(preview, reply_markup=broadcast_group_confirm_keyboard())


@router.callback_query(F.data == "admin:broadcast_group:confirm")
async def admin_broadcast_group_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    body = data.get("broadcast_text")
    group_id = data.get("broadcast_group_id")
    if not body or group_id is None:
        await callback.answer("Сессия рассылки истекла", show_alert=True)
        return

    async with async_session() as db:
        users = await get_announcement_recipients(db, group_id)

    if not users:
        await callback.answer("В группе пока нет участников", show_alert=True)
        return

    sent, blocked, failed = await send_bot_user_broadcast(users, body)

    await state.set_state(AdminStates.MENU)
    await state.update_data(edit_mode=False)
    result = f"Сообщение отправлено: {sent} из {len(users)}."
    if blocked:
        result += f" Заблокировали бота: {blocked}."
    if failed:
        result += " Есть недоставленные сообщения (см. логи сервера)."
    await _finish_admin_callback(callback, result, reply_markup=admin_menu_keyboard())
