from __future__ import annotations

import io
import logging
from datetime import date, time

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .common import (
    _COVER_RETRY_HINT,
    _PRICE_PROMPT,
    _PRICE_RETRY,
    _description_line,
    _price_confirm_line,
    _prompt_create_approval,
    _prompt_create_audience,
    _prompt_create_featured,
    _save_cover_from_message,
    _telegram_file_too_large,
    is_admin,
)
from app.bot.keyboards import (
    admin_menu_keyboard,
    create_confirm_keyboard,
    skip_capacity_keyboard,
    skip_image_keyboard,
    skip_price_keyboard,
)
from app.bot.parsers import (
    format_capacity_ru,
    format_date_ru,
    format_time_ru,
    parse_capacity,
    parse_date,
    parse_time,
    plain_user_text,
)
from app.bot.states import AdminStates
from app.database import async_session
from app.services.access_groups import get_announcement_recipients, get_group_by_id
from app.services.event_announcement import send_new_event_announcement
from app.services.events import create_event
from app.services.storage import (
    DEFAULT_COVER_URL,
    cover_filename_from_document,
    image_too_large_message,
    normalize_cover_image_url,
)
from app.services.users import get_or_create_user
from app.utils.pricing import parse_ruble_price

logger = logging.getLogger(__name__)
router = Router()

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
    await state.set_state(AdminStates.CREATE_PRICE)
    await message.answer(_PRICE_PROMPT, reply_markup=skip_price_keyboard())

@router.message(AdminStates.CREATE_PRICE)
async def create_price(message: Message, state: FSMContext):
    parsed = parse_ruble_price(message.text or "")
    if parsed is None:
        await message.answer(_PRICE_RETRY, reply_markup=skip_price_keyboard())
        return
    await state.update_data(price_amount_minor=parsed, price_currency="RUB")
    await state.set_state(AdminStates.CREATE_DESCRIPTION)
    await message.answer("Введите описание события:")

@router.callback_query(F.data == "admin:skip_price", AdminStates.CREATE_PRICE)
async def create_skip_price(callback: CallbackQuery, state: FSMContext):
    await state.update_data(price_amount_minor=None, price_currency=None)
    await state.set_state(AdminStates.CREATE_DESCRIPTION)
    await callback.message.edit_text("Введите описание события:")
    await callback.answer()

@router.message(AdminStates.CREATE_DESCRIPTION)
async def create_description(message: Message, state: FSMContext):
    description = plain_user_text(message.text, message.caption)
    if not description:
        await message.answer("Введите описание события текстом:")
        return
    await state.update_data(description=description)
    await state.set_state(AdminStates.CREATE_CAPACITY)
    await message.answer(
        "Введите лимит мест (число) или выберите «Без лимита»:",
        reply_markup=skip_capacity_keyboard(),
    )

@router.callback_query(F.data == "admin:skip_capacity", AdminStates.CREATE_CAPACITY)
async def create_skip_capacity(callback: CallbackQuery, state: FSMContext):
    await state.update_data(max_participants=None)
    await _prompt_create_approval(callback.message, state, edit=True)
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
    await _prompt_create_approval(message, state, edit=False)

@router.callback_query(F.data.startswith("admin:approval:"), AdminStates.CREATE_APPROVAL)
async def create_approval_chosen(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    token = callback.data.split(":")[-1]
    if token not in {"open", "required"}:
        await callback.answer("Некорректный выбор", show_alert=True)
        return
    await state.update_data(requires_approval=token == "required")
    await _prompt_create_audience(callback.message, state, edit=True)
    await callback.answer()

@router.callback_query(F.data.startswith("admin:audience:"), AdminStates.CREATE_AUDIENCE)
async def create_audience_chosen(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    token = callback.data.split(":")[-1]
    if token == "all":
        await state.update_data(audience_group_id=None, audience_label="Все участники")
    else:
        group_id = int(token)
        async with async_session() as db:
            group = await get_group_by_id(db, group_id)
        if group is None:
            await callback.answer("Группа не найдена", show_alert=True)
            return
        await state.update_data(audience_group_id=group.group_id, audience_label=group.name)

    await _prompt_create_featured(callback.message, state, edit=True)
    await callback.answer()

@router.callback_query(F.data.startswith("admin:featured:"), AdminStates.CREATE_FEATURED)
async def create_featured_chosen(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    token = callback.data.split(":")[-1]
    if token not in {"yes", "no"}:
        await callback.answer("Некорректный выбор", show_alert=True)
        return

    await state.update_data(is_featured=token == "yes")
    await state.set_state(AdminStates.CREATE_IMAGE)
    await callback.message.edit_text(
        "Загрузите обложку (JPEG или PNG, до 5 МБ) или пропустите:",
        reply_markup=skip_image_keyboard(),
    )
    await callback.answer()

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
    audience_group_id = data.get("audience_group_id")
    audience_name = data.get("audience_label") or "Все участники"
    featured_label = "да" if data.get("is_featured") else "нет"
    approval_label = "по заявке" if data.get("requires_approval") else "сразу"
    async with async_session() as db:
        recipients = await get_announcement_recipients(db, audience_group_id)
        recipient_count = len(recipients)
    text = (
        f"Проверьте данные:\n\n"
        f"📌 {data['name']}\n"
        f"📅 {format_date_ru(event_date)}, {format_time_ru(event_time)}\n"
        f"📍 {data['location']}\n"
        f"{_price_confirm_line(data)}"
        f"📝 {_description_line(data.get('description'))}\n"
        f"👥 Лимит мест: {format_capacity_ru(data.get('max_participants'))}\n"
        f"⏳ Запись: {approval_label}\n"
        f"🔐 Аудитория: {audience_name}\n"
        f"🖼️ Слайдер: {featured_label}\n\n"
        f"Получателей уведомления: {recipient_count}"
    )
    await state.set_state(AdminStates.CREATE_CONFIRM)
    markup = create_confirm_keyboard(audience_is_group=audience_group_id is not None)
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)

async def _answer_create_callback(callback: CallbackQuery) -> None:
    """Answer immediately so Telegram does not retry a long create+broadcast."""
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass

async def _edit_create_progress(callback: CallbackQuery, text: str) -> None:
    if callback.message is None:
        return
    try:
        await callback.message.edit_text(text)
    except TelegramBadRequest:
        pass

async def _finish_event_create(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    notify: bool,
) -> None:
    await _answer_create_callback(callback)
    await _edit_create_progress(
        callback,
        "Создаём событие и рассылаем анонс…" if notify else "Создаём событие…",
    )

    data = await state.get_data()
    audience_group_id = data.get("audience_group_id")
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
            audience_group_id=audience_group_id,
            is_featured=bool(data.get("is_featured")),
            requires_approval=bool(data.get("requires_approval")),
            price_amount_minor=data.get("price_amount_minor"),
            price_currency=data.get("price_currency"),
        )
        users = await get_announcement_recipients(db, audience_group_id)

    event_date = date.fromisoformat(data["event_date"])
    result = f"Событие создано: {event.name} на {format_date_ru(event_date)} ✅"

    if notify:
        audience_name = data.get("audience_label") or "Все участники"
        if not users:
            result += f"\n\nУведомление не отправлено: в аудитории «{audience_name}» пока нет пользователей."
        else:
            try:
                bot_user = await callback.bot.get_me()
                if not bot_user.username:
                    result += "\n\nУведомление не отправлено: не удалось определить имя бота."
                else:
                    sent, blocked, failed = await send_new_event_announcement(
                        users,
                        event,
                        bot_user.username,
                    )
                    result += f"\n\nАнонс отправлен: {sent} из {len(users)} ({audience_name})."
                    if blocked:
                        result += f" Заблокировали бота: {blocked}."
                    if failed:
                        result += " Есть недоставленные сообщения (см. логи сервера)."
            except Exception:
                logger.exception("Failed to send new event announcement for event_id=%s", event.event_id)
                result += "\n\nУведомление не отправлено: ошибка при рассылке (см. логи сервера)."

    await state.clear()
    await state.set_state(AdminStates.MENU)
    if callback.message is not None:
        try:
            await callback.message.edit_text(result, reply_markup=admin_menu_keyboard())
        except TelegramBadRequest:
            await callback.message.answer(result, reply_markup=admin_menu_keyboard())

@router.callback_query(F.data == "admin:create:confirm")
async def create_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _finish_event_create(callback, state, notify=False)

@router.callback_query(F.data == "admin:create:confirm:notify")
async def create_confirm_notify(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _finish_event_create(callback, state, notify=True)
