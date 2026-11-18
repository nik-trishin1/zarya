from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .common import (
    _description_line,
    _event_price_line,
    is_admin,
)
from app.bot.keyboards import (
    admin_menu_keyboard,
    back_to_archive_event_keyboard,
    back_to_event_keyboard,
    back_to_menu_keyboard,
    delete_confirm_keyboard,
    event_archive_keyboard,
    event_manage_keyboard,
    pending_list_keyboard,
)
from app.bot.participants import format_participants_message
from app.bot.parsers import format_date_ru, format_guest_count, format_time_ru
from app.bot.states import AdminStates
from app.database import async_session
from app.services.access_groups import audience_label, get_group_by_id, list_access_groups
from app.services.events import (
    delete_event,
    get_all_events_admin,
    get_event_by_id,
    get_event_maybe_users,
    get_event_pending_users,
    get_event_registration_parties,
    get_past_events_admin,
    is_event_past,
)

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(
            "У вас нет доступа к панели администратора.\n\n"
            f"Ваш Telegram ID: `{message.from_user.id}`\n"
            "Отправьте `/myid` и добавьте этот ID в `ADMIN_TELEGRAM_IDS` на Railway.",
            parse_mode="Markdown",
        )
        return

    await state.set_state(AdminStates.MENU)
    await message.answer("Панель администратора 🌅", reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text("Панель администратора 🌅", reply_markup=admin_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text("Действие отменено.", reply_markup=admin_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin:manage")
async def admin_manage(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as db:
        events = await get_all_events_admin(db)

    if not events:
        await callback.message.edit_text(
            "Нет предстоящих событий.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    buttons = []
    async with async_session() as db:
        groups = {g.group_id: g for g in await list_access_groups(db)}
    for event, reg_count in events:
        aud = audience_label(groups.get(event.audience_group_id) if event.audience_group_id else None)
        label = (
            f"{event.name} [{aud}] | {format_date_ru(event.date)} | "
            f"{format_guest_count(reg_count, event.max_participants)}"
        )
        buttons.append([InlineKeyboardButton(text=label[:64], callback_data=f"admin:detail:{event.event_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ В меню", callback_data="admin:menu")])

    await state.set_state(AdminStates.MANAGE_LIST)
    await callback.message.edit_text(
        "Выберите событие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


# --- Archive (past events) ---

@router.callback_query(F.data == "admin:archive")
async def admin_archive(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as db:
        events = await get_past_events_admin(db)

    if not events:
        await callback.message.edit_text(
            "Архив пуст.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    buttons = []
    async with async_session() as db:
        groups = {g.group_id: g for g in await list_access_groups(db)}
    for event, reg_count in events:
        aud = audience_label(groups.get(event.audience_group_id) if event.audience_group_id else None)
        label = (
            f"{event.name} [{aud}] | {format_date_ru(event.date)} | "
            f"{format_guest_count(reg_count, event.max_participants)}"
        )
        buttons.append(
            [InlineKeyboardButton(text=label[:64], callback_data=f"admin:archive:detail:{event.event_id}")]
        )
    buttons.append([InlineKeyboardButton(text="◀️ В меню", callback_data="admin:menu")])

    await state.set_state(AdminStates.ARCHIVE_LIST)
    await callback.message.edit_text(
        "Архив событий:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:archive:detail:"))
async def admin_archive_event_detail(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        archive_events = await get_past_events_admin(db)
        event_data = next(((e, c) for e, c in archive_events if e.event_id == event_id), None)

    if event_data is None:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    event, reg_count = event_data
    async with async_session() as db:
        group = None
        if event.audience_group_id is not None:
            group = await get_group_by_id(db, event.audience_group_id)
    text = (
        f"Событие: {event.name}\n"
        f"Дата: {format_date_ru(event.date)}, {format_time_ru(event.time)}\n"
        f"Место: {event.location}\n"
        f"{_event_price_line(event)}"
        f"Аудитория: {audience_label(group)}\n"
        f"{format_guest_count(reg_count, event.max_participants)}\n"
        f"Статус: Завершено\n"
        f"Описание: {_description_line(event.description)}"
    )
    await state.set_state(AdminStates.ARCHIVE_DETAIL)
    await state.update_data(event_id=event_id, archive_context=True)
    await callback.message.edit_text(text, reply_markup=event_archive_keyboard(event_id))
    await callback.answer()


@router.callback_query(F.data.regexp(r"^admin:archive:registrations:\d+$"))
async def admin_archive_event_registrations(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None or not is_event_past(event):
            await callback.answer("Событие не найдено", show_alert=True)
            return
        parties = await get_event_registration_parties(db, event_id)
        maybe_users = await get_event_maybe_users(db, event_id)
        pending_users = await get_event_pending_users(db, event_id)

    await state.set_state(AdminStates.ARCHIVE_DETAIL)
    await state.update_data(event_id=event_id, archive_context=True)
    text = format_participants_message(
        event.name, parties, maybe_users=maybe_users, pending_users=pending_users
    )
    await callback.message.edit_text(text, reply_markup=back_to_archive_event_keyboard(event_id))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:detail:"))
async def admin_event_detail(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        detail_events = await get_all_events_admin(db)
        event_data = next(((e, c) for e, c in detail_events if e.event_id == event_id), None)

    if event_data is None:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    event, reg_count = event_data
    async with async_session() as db:
        group = None
        if event.audience_group_id is not None:
            group = await get_group_by_id(db, event.audience_group_id)
    text = (
        f"Событие: {event.name}\n"
        f"Дата: {format_date_ru(event.date)}, {format_time_ru(event.time)}\n"
        f"Место: {event.location}\n"
        f"{_event_price_line(event)}"
        f"Аудитория: {audience_label(group)}\n"
        f"{format_guest_count(reg_count, event.max_participants)}\n"
        f"Описание: {_description_line(event.description)}"
    )
    await state.set_state(AdminStates.MANAGE_DETAIL)
    await state.update_data(event_id=event_id)
    await callback.message.edit_text(text, reply_markup=event_manage_keyboard(event_id))
    await callback.answer()


@router.callback_query(F.data.regexp(r"^admin:registrations:\d+$"))
async def admin_event_registrations(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        parties = await get_event_registration_parties(db, event_id)
        maybe_users = await get_event_maybe_users(db, event_id)
        pending_users = await get_event_pending_users(db, event_id)

    await state.set_state(AdminStates.MANAGE_DETAIL)
    await state.update_data(event_id=event_id)
    text = format_participants_message(
        event.name, parties, maybe_users=maybe_users, pending_users=pending_users
    )
    pending_only = [user for user, _ in pending_users]
    markup = (
        pending_list_keyboard(event_id, pending_only, back_callback=f"admin:detail:{event_id}")
        if pending_only
        else back_to_event_keyboard(event_id)
    )
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("admin:delete:"))
async def admin_delete_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("admin:delete_confirm:"):
        return
    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
    if event is None:
        await callback.answer("Событие не найдено", show_alert=True)
        return
    if is_event_past(event):
        await callback.answer("Нельзя удалить завершённое событие", show_alert=True)
        return
    await state.set_state(AdminStates.DELETE_CONFIRM)
    await callback.message.edit_text(
        "Вы уверены? Это действие нельзя отменить.",
        reply_markup=delete_confirm_keyboard(event_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete_confirm:"))
async def admin_delete_confirm(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        if is_event_past(event):
            await callback.answer("Нельзя удалить завершённое событие", show_alert=True)
            return
        name = event.name
        await delete_event(db, event)

    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text(
        f"Событие удалено: {name}",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()
