from __future__ import annotations

import io
import logging
from datetime import date, time

from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.bot.keyboards import (
    admin_menu_keyboard,
    back_to_event_keyboard,
    back_to_menu_keyboard,
    broadcast_confirm_keyboard,
    confirm_keyboard,
    create_confirm_keyboard,
    delete_confirm_keyboard,
    edit_keep_keyboard,
    event_manage_keyboard,
    skip_capacity_keyboard,
    skip_image_keyboard,
)
from app.bot.participants import format_participants_message
from app.bot.parsers import format_capacity_ru, format_date_ru, format_guest_count, format_time_ru, parse_capacity, parse_date, parse_time
from app.bot.states import AdminStates
from app.config import get_settings
from app.database import async_session
from app.services.users import get_all_users, get_or_create_user
from app.services.events import (
    create_event,
    delete_event,
    get_all_events_admin,
    get_event_by_id,
    get_event_registered_users,
    update_event,
)
from app.services.event_announcement import send_new_event_announcement
from app.services.participant_broadcast import (
    build_broadcast_preview,
    send_participant_broadcast,
    validate_broadcast_body,
)
from app.services.storage import (
    DEFAULT_COVER_URL,
    MAX_FILE_SIZE,
    cover_filename_from_document,
    image_too_large_message,
    normalize_cover_image_url,
    save_cover_image_bytes,
)

logger = logging.getLogger(__name__)
router = Router()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


_COVER_RETRY_HINT = (
    "\n\nЗагрузите другое изображение (JPEG или PNG, до 5 МБ) или нажмите «Пропустить»."
)


async def _save_cover_from_message(message: Message, content: bytes, filename: str) -> str | None:
    try:
        return await save_cover_image_bytes(content, filename)
    except ValueError as e:
        await message.answer(f"{e}{_COVER_RETRY_HINT}")
        return None


def _telegram_file_too_large(file_size: int | None) -> bool:
    return file_size is not None and file_size > MAX_FILE_SIZE


async def _edit_or_answer(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup)


async def _finish_admin_callback(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if callback.message is not None:
        await _edit_or_answer(callback.message, text, reply_markup=reply_markup)
    await callback.answer()


async def _send_edit_prompt(
    message: Message,
    state: FSMContext,
    *,
    text: str,
    next_state: AdminStates,
    reply_markup: InlineKeyboardMarkup | None = None,
    edit: bool = False,
) -> None:
    await state.set_state(next_state)
    if edit:
        await _edit_or_answer(message, text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


async def _goto_edit_name(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    await _send_edit_prompt(
        message,
        state,
        text=f"Текущее название: {data['name']}\n\nВведите новое название или нажмите «Оставить»:",
        next_state=AdminStates.EDIT_NAME,
        reply_markup=edit_keep_keyboard(),
        edit=edit,
    )


async def _goto_edit_date(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    event_date = date.fromisoformat(data["event_date"])
    await _send_edit_prompt(
        message,
        state,
        text=(
            f"Текущая дата: {format_date_ru(event_date)}\n\n"
            "Введите новую дату или нажмите «Оставить»:"
        ),
        next_state=AdminStates.EDIT_DATE,
        reply_markup=edit_keep_keyboard(),
        edit=edit,
    )


async def _goto_edit_time(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    event_time = time.fromisoformat(data["event_time"])
    await _send_edit_prompt(
        message,
        state,
        text=(
            f"Текущее время: {format_time_ru(event_time)}\n\n"
            "Введите новое время или нажмите «Оставить»:"
        ),
        next_state=AdminStates.EDIT_TIME,
        reply_markup=edit_keep_keyboard(),
        edit=edit,
    )


async def _goto_edit_location(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    await _send_edit_prompt(
        message,
        state,
        text=f"Текущее место: {data['location']}\n\nВведите новое место или нажмите «Оставить»:",
        next_state=AdminStates.EDIT_LOCATION,
        reply_markup=edit_keep_keyboard(),
        edit=edit,
    )


async def _goto_edit_description(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    await _send_edit_prompt(
        message,
        state,
        text=(
            f"Текущее описание: {data.get('description', '')}\n\n"
            "Введите новое описание или нажмите «Оставить»:"
        ),
        next_state=AdminStates.EDIT_DESCRIPTION,
        reply_markup=edit_keep_keyboard(),
        edit=edit,
    )


async def _goto_edit_image(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    await _send_edit_prompt(
        message,
        state,
        text="Загрузите новую обложку (JPEG или PNG, до 5 МБ) или нажмите «Оставить текущую»:",
        next_state=AdminStates.EDIT_IMAGE,
        reply_markup=skip_image_keyboard(keep_current=True),
        edit=edit,
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_user = message.from_user
    if tg_user:
        async with async_session() as db:
            await get_or_create_user(db, tg_user.id, tg_user.username, tg_user.first_name)

    await message.answer(
        "Привет! 🌅\n"
        "Мы ждем тебя на наших скорых встречах.\n"
        "Нажми кнопку меню, чтобы посмотреть предстоящие события!",
    )


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    user = message.from_user
    if user:
        async with async_session() as db:
            await get_or_create_user(db, user.id, user.username, user.first_name)

    await message.answer(
        f"Ваш Telegram ID: `{user.id}`\n\n"
        "Добавьте его в `ADMIN_TELEGRAM_IDS` на сервере (Railway → Variables), "
        "если `/admin` отвечает «нет доступа».",
        parse_mode="Markdown",
    )


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


# --- Create event flow ---

@router.callback_query(F.data == "admin:create")
async def admin_create_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.CREATE_NAME)
    await state.update_data(edit_mode=False)
    await callback.message.edit_text("Введите название события:")
    await callback.answer()


@router.message(AdminStates.CREATE_NAME)
async def create_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.CREATE_DATE)
    await message.answer("Введите дату (например, 28.06.2026):")


@router.message(AdminStates.CREATE_DATE)
async def create_date(message: Message, state: FSMContext):
    parsed = parse_date(message.text or "")
    if parsed is None:
        await message.answer("Не удалось распознать дату. Формат: ДД.ММ.ГГГГ")
        return
    await state.update_data(event_date=parsed.isoformat())
    await state.set_state(AdminStates.CREATE_TIME)
    await message.answer("Введите время (например, 19:00):")


@router.message(AdminStates.CREATE_TIME)
async def create_time(message: Message, state: FSMContext):
    parsed = parse_time(message.text or "")
    if parsed is None:
        await message.answer("Не удалось распознать время. Формат: ЧЧ:ММ")
        return
    await state.update_data(event_time=parsed.isoformat())
    await state.set_state(AdminStates.CREATE_LOCATION)
    await message.answer("Введите место проведения:")


@router.message(AdminStates.CREATE_LOCATION)
async def create_location(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Место слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(location=message.text.strip())
    await state.set_state(AdminStates.CREATE_DESCRIPTION)
    await message.answer("Введите описание события:")


@router.message(AdminStates.CREATE_DESCRIPTION)
async def create_description(message: Message, state: FSMContext):
    await state.update_data(description=(message.text or "").strip())
    await state.set_state(AdminStates.CREATE_CAPACITY)
    await message.answer(
        "Введите лимит мест (число) или выберите «Без лимита»:",
        reply_markup=skip_capacity_keyboard(),
    )


@router.callback_query(F.data == "admin:skip_capacity", AdminStates.CREATE_CAPACITY)
async def create_skip_capacity(callback: CallbackQuery, state: FSMContext):
    await state.update_data(max_participants=None)
    await state.set_state(AdminStates.CREATE_IMAGE)
    await callback.message.edit_text(
        "Загрузите обложку (JPEG или PNG, до 5 МБ) или пропустите:",
        reply_markup=skip_image_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.CREATE_CAPACITY)
async def create_capacity(message: Message, state: FSMContext):
    parsed = parse_capacity(message.text or "")
    if parsed is None:
        await message.answer(
            "Введите целое число от 1 до 10000 или нажмите «Без лимита»:",
            reply_markup=skip_capacity_keyboard(),
        )
        return
    await state.update_data(max_participants=parsed)
    await state.set_state(AdminStates.CREATE_IMAGE)
    await message.answer(
        "Загрузите обложку (JPEG или PNG, до 5 МБ) или пропустите:",
        reply_markup=skip_image_keyboard(),
    )


@router.message(AdminStates.CREATE_IMAGE, F.photo)
async def create_image_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    if _telegram_file_too_large(photo.file_size):
        await message.answer(f"{image_too_large_message()}{_COVER_RETRY_HINT}")
        return
    file = await message.bot.get_file(photo.file_id)
    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    cover_url = await _save_cover_from_message(message, buffer.getvalue(), "cover.jpg")
    if cover_url is None:
        return
    await state.update_data(cover_image_url=cover_url)
    await show_create_confirm(message, state)


@router.message(AdminStates.CREATE_IMAGE, F.document)
async def create_image_document(message: Message, state: FSMContext):
    doc = message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await message.answer("Пожалуйста, загрузите изображение (JPEG или PNG).")
        return
    if _telegram_file_too_large(doc.file_size):
        await message.answer(f"{image_too_large_message()}{_COVER_RETRY_HINT}")
        return
    file = await message.bot.get_file(doc.file_id)
    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    cover_url = await _save_cover_from_message(
        message, buffer.getvalue(), cover_filename_from_document(doc.file_name, doc.mime_type)
    )
    if cover_url is None:
        return
    await state.update_data(cover_image_url=cover_url)
    await show_create_confirm(message, state)


@router.callback_query(F.data == "admin:skip_image", AdminStates.CREATE_IMAGE)
async def create_skip_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cover_image_url=DEFAULT_COVER_URL)
    await show_create_confirm(callback.message, state, edit=True)
    await callback.answer()


async def show_create_confirm(message: Message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    event_date = date.fromisoformat(data["event_date"])
    event_time = time.fromisoformat(data["event_time"])
    async with async_session() as db:
        user_count = len(await get_all_users(db))
    text = (
        f"Проверьте данные:\n\n"
        f"📌 {data['name']}\n"
        f"📅 {format_date_ru(event_date)}, {format_time_ru(event_time)}\n"
        f"📍 {data['location']}\n"
        f"📝 {data.get('description', '')}\n"
        f"👥 Лимит мест: {format_capacity_ru(data.get('max_participants'))}\n\n"
        f"Пользователей в боте: {user_count}"
    )
    await state.set_state(AdminStates.CREATE_CONFIRM)
    if edit:
        await message.edit_text(text, reply_markup=create_confirm_keyboard())
    else:
        await message.answer(text, reply_markup=create_confirm_keyboard())


async def _finish_event_create(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    notify_all: bool,
) -> None:
    data = await state.get_data()
    async with async_session() as db:
        admin_user = await get_or_create_user(
            db,
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.first_name,
        )
        event = await create_event(
            db,
            name=data["name"],
            description=data.get("description", ""),
            event_date=date.fromisoformat(data["event_date"]),
            event_time=time.fromisoformat(data["event_time"]),
            location=data["location"],
            cover_image_url=normalize_cover_image_url(data.get("cover_image_url")),
            admin_user=admin_user,
            max_participants=data.get("max_participants"),
        )
        users = await get_all_users(db)

    event_date = date.fromisoformat(data["event_date"])
    result = f"Событие создано: {event.name} на {format_date_ru(event_date)} ✅"

    if notify_all:
        if not users:
            result += "\n\nУведомление не отправлено: в боте пока нет пользователей."
        else:
            bot_user = await callback.bot.get_me()
            if not bot_user.username:
                result += "\n\nУведомление не отправлено: не удалось определить имя бота."
            else:
                sent, blocked, failed = await send_new_event_announcement(
                    users,
                    event,
                    bot_user.username,
                )
                result += f"\n\nАнонс отправлен: {sent} из {len(users)}."
                if blocked:
                    result += f" Заблокировали бота: {blocked}."
                if failed:
                    result += " Есть недоставленные сообщения (см. логи сервера)."

    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text(result, reply_markup=admin_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:create:confirm")
async def create_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _finish_event_create(callback, state, notify_all=False)


@router.callback_query(F.data == "admin:create:confirm:notify")
async def create_confirm_notify(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _finish_event_create(callback, state, notify_all=True)


# --- Manage events ---

@router.callback_query(F.data == "admin:manage")
async def admin_manage(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as db:
        events = await get_all_events_admin(db)

    if not events:
        await callback.message.edit_text(
            "Событий пока нет.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    buttons = []
    for event, reg_count in events:
        label = f"{event.name} | {format_date_ru(event.date)} | {format_guest_count(reg_count, event.max_participants)}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"admin:detail:{event.event_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ В меню", callback_data="admin:menu")])

    await state.set_state(AdminStates.MANAGE_LIST)
    await callback.message.edit_text(
        "Выберите событие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
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
    text = (
        f"Событие: {event.name}\n"
        f"Дата: {format_date_ru(event.date)}, {format_time_ru(event.time)}\n"
        f"Место: {event.location}\n"
        f"{format_guest_count(reg_count, event.max_participants)}\n\n"
        f"{event.description}"
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
        users = await get_event_registered_users(db, event_id)

    await state.set_state(AdminStates.MANAGE_DETAIL)
    await state.update_data(event_id=event_id)
    text = format_participants_message(event.name, users)
    await callback.message.edit_text(text, reply_markup=back_to_event_keyboard(event_id))
    await callback.answer()


# --- Broadcast to participants ---

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


# --- Edit event ---

@router.callback_query(F.data == "admin:edit:confirm")
async def edit_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    event_id = data.get("event_id")
    if event_id is None or not data.get("edit_mode"):
        await callback.answer(
            "Сессия редактирования истекла. Откройте событие и нажмите «Редактировать» снова.",
            show_alert=True,
        )
        return

    try:
        async with async_session() as db:
            event = await get_event_by_id(db, event_id)
            if event is None:
                await callback.answer("Событие не найдено", show_alert=True)
                return
            await update_event(
                db,
                event,
                name=data["name"],
                description=data.get("description", ""),
                date=date.fromisoformat(data["event_date"]),
                time=time.fromisoformat(data["event_time"]),
                location=data["location"],
                cover_image_url=normalize_cover_image_url(data.get("cover_image_url")),
            )
    except Exception:
        logger.exception("Failed to confirm event edit for event_id=%s", event_id)
        await callback.answer("Не удалось сохранить изменения", show_alert=True)
        return

    await state.clear()
    await state.set_state(AdminStates.MENU)
    await _finish_admin_callback(
        callback,
        f"Событие обновлено: {data['name']} ✅",
        reply_markup=admin_menu_keyboard(),
    )


@router.callback_query(F.data.regexp(r"^admin:edit:\d+$"))
async def admin_edit_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
    if event is None:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    await state.update_data(
        event_id=event_id,
        name=event.name,
        event_date=event.date.isoformat(),
        event_time=event.time.isoformat(),
        location=event.location,
        description=event.description,
        cover_image_url=normalize_cover_image_url(event.cover_image_url),
        edit_mode=True,
    )
    if callback.message is None:
        await callback.answer()
        return
    await _goto_edit_name(callback.message, state, edit=True)
    await callback.answer()


@router.callback_query(F.data == "admin:edit:keep")
async def edit_keep_current(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("edit_mode"):
        await callback.answer("Сессия редактирования истекла", show_alert=True)
        return
    if callback.message is None:
        await callback.answer()
        return

    current_state = await state.get_state()
    if current_state == AdminStates.EDIT_NAME.state:
        await _goto_edit_date(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_DATE.state:
        await _goto_edit_time(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_TIME.state:
        await _goto_edit_location(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_LOCATION.state:
        await _goto_edit_description(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_DESCRIPTION.state:
        await _goto_edit_image(callback.message, state, edit=True)
    else:
        await callback.answer()
        return

    await callback.answer()


@router.message(AdminStates.EDIT_NAME)
async def edit_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз или нажмите «Оставить»:")
        return
    await state.update_data(name=message.text.strip())
    await _goto_edit_date(message, state)


@router.message(AdminStates.EDIT_DATE)
async def edit_date(message: Message, state: FSMContext):
    parsed = parse_date(message.text or "")
    if parsed is None:
        await message.answer("Не удалось распознать дату. Формат: ДД.ММ.ГГГГ")
        return
    await state.update_data(event_date=parsed.isoformat())
    await _goto_edit_time(message, state)


@router.message(AdminStates.EDIT_TIME)
async def edit_time(message: Message, state: FSMContext):
    parsed = parse_time(message.text or "")
    if parsed is None:
        await message.answer("Не удалось распознать время. Формат: ЧЧ:ММ")
        return
    await state.update_data(event_time=parsed.isoformat())
    await _goto_edit_location(message, state)


@router.message(AdminStates.EDIT_LOCATION)
async def edit_location(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Место слишком короткое. Попробуйте ещё раз или нажмите «Оставить»:")
        return
    await state.update_data(location=message.text.strip())
    await _goto_edit_description(message, state)


@router.message(AdminStates.EDIT_DESCRIPTION)
async def edit_description(message: Message, state: FSMContext):
    await state.update_data(description=(message.text or "").strip())
    await _goto_edit_image(message, state)


@router.message(AdminStates.EDIT_IMAGE, F.photo)
async def edit_image_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    if _telegram_file_too_large(photo.file_size):
        await message.answer(f"{image_too_large_message()}{_COVER_RETRY_HINT}")
        return
    file = await message.bot.get_file(photo.file_id)
    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    cover_url = await _save_cover_from_message(message, buffer.getvalue(), "cover.jpg")
    if cover_url is None:
        return
    await state.update_data(cover_image_url=cover_url)
    await show_edit_confirm(message, state)


@router.message(AdminStates.EDIT_IMAGE, F.document)
async def edit_image_document(message: Message, state: FSMContext):
    doc = message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await message.answer("Пожалуйста, загрузите изображение (JPEG или PNG).")
        return
    if _telegram_file_too_large(doc.file_size):
        await message.answer(f"{image_too_large_message()}{_COVER_RETRY_HINT}")
        return
    file = await message.bot.get_file(doc.file_id)
    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    cover_url = await _save_cover_from_message(
        message, buffer.getvalue(), cover_filename_from_document(doc.file_name, doc.mime_type)
    )
    if cover_url is None:
        return
    await state.update_data(cover_image_url=cover_url)
    await show_edit_confirm(message, state)


@router.callback_query(F.data == "admin:skip_image", AdminStates.EDIT_IMAGE)
async def edit_skip_image(callback: CallbackQuery, state: FSMContext):
    await show_edit_confirm(callback.message, state, edit=True)
    await callback.answer()


async def show_edit_confirm(message: Message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    event_date = date.fromisoformat(data["event_date"])
    event_time = time.fromisoformat(data["event_time"])
    text = (
        f"Проверьте изменения:\n\n"
        f"📌 {data['name']}\n"
        f"📅 {format_date_ru(event_date)}, {format_time_ru(event_time)}\n"
        f"📍 {data['location']}\n"
        f"📝 {data.get('description', '')}\n"
    )
    await state.set_state(AdminStates.EDIT_CONFIRM)
    keyboard = confirm_keyboard("edit")
    if edit:
        await _edit_or_answer(message, text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


# --- Delete event ---

@router.callback_query(F.data.startswith("admin:delete:"))
async def admin_delete_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("admin:delete_confirm:"):
        return
    event_id = int(callback.data.split(":")[-1])
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
        name = event.name
        await delete_event(db, event)

    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text(
        f"Событие удалено: {name}",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


def create_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    return dp


async def run_bot():
    settings = get_settings()
    if not settings.bot_token_configured:
        logger.warning("BOT_TOKEN not configured, bot will not start")
        return

    bot = Bot(token=settings.bot_token.strip())
    dp = create_dispatcher()
    logger.info("Telegram bot polling started (webapp_url=%s)", settings.webapp_url)
    await dp.start_polling(bot)
