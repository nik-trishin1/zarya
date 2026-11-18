from __future__ import annotations

import io
import logging
from datetime import date, time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .common import (
    _COVER_RETRY_HINT,
    _PRICE_RETRY,
    _description_line,
    _edit_or_answer,
    _finish_admin_callback,
    _goto_edit_date,
    _goto_edit_description,
    _goto_edit_image,
    _goto_edit_location,
    _goto_edit_name,
    _goto_edit_price,
    _goto_edit_time,
    _price_confirm_line,
    _prompt_edit_featured,
    _save_cover_from_message,
    _telegram_file_too_large,
    is_admin,
)
from app.bot.keyboards import (
    admin_menu_keyboard,
    confirm_keyboard,
    edit_keep_keyboard,
    skip_image_keyboard,
    skip_price_keyboard,
)
from app.bot.parsers import format_date_ru, format_time_ru, parse_date, parse_time, plain_user_text
from app.bot.states import AdminStates
from app.database import async_session
from app.services.events import get_event_by_id, is_event_past, update_event
from app.services.storage import (
    cover_filename_from_document,
    image_too_large_message,
    normalize_cover_image_url,
)
from app.utils.pricing import parse_ruble_price

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("admin:featured:"), AdminStates.EDIT_FEATURED)
async def edit_featured_chosen(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("edit_mode"):
        await callback.answer("Сессия редактирования истекла", show_alert=True)
        return

    token = callback.data.split(":")[-1]
    if token not in {"yes", "no"}:
        await callback.answer("Некорректный выбор", show_alert=True)
        return

    await state.update_data(is_featured=token == "yes")
    if callback.message is None:
        await callback.answer()
        return
    await _goto_edit_image(callback.message, state, edit=True)
    await callback.answer()

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
            if is_event_past(event):
                await callback.answer("Нельзя редактировать завершённые события", show_alert=True)
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
                is_featured=bool(data.get("is_featured")),
                price_amount_minor=data.get("price_amount_minor"),
                price_currency=data.get("price_currency"),
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
    if is_event_past(event):
        await callback.answer("Нельзя редактировать завершённые события", show_alert=True)
        return

    await state.update_data(
        event_id=event_id,
        name=event.name,
        event_date=event.date.isoformat(),
        event_time=event.time.isoformat(),
        location=event.location,
        description=event.description,
        cover_image_url=normalize_cover_image_url(event.cover_image_url),
        is_featured=bool(getattr(event, "is_featured", False)),
        price_amount_minor=getattr(event, "price_amount_minor", None),
        price_currency=getattr(event, "price_currency", None),
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
        await _goto_edit_price(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_PRICE.state:
        await _goto_edit_description(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_DESCRIPTION.state:
        await _prompt_edit_featured(callback.message, state, edit=True)
    elif current_state == AdminStates.EDIT_FEATURED.state:
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
    await _goto_edit_price(message, state)


@router.message(AdminStates.EDIT_PRICE)
async def edit_price(message: Message, state: FSMContext):
    parsed = parse_ruble_price(message.text or "")
    if parsed is None:
        await message.answer(_PRICE_RETRY, reply_markup=skip_price_keyboard(keep_current=True))
        return
    await state.update_data(price_amount_minor=parsed, price_currency="RUB")
    await _goto_edit_description(message, state)


@router.callback_query(F.data == "admin:skip_price", AdminStates.EDIT_PRICE)
async def edit_skip_price(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    data = await state.get_data()
    if not data.get("edit_mode"):
        await callback.answer("Сессия редактирования истекла", show_alert=True)
        return
    await state.update_data(price_amount_minor=None, price_currency=None)
    if callback.message is None:
        await callback.answer()
        return
    await _goto_edit_description(callback.message, state, edit=True)
    await callback.answer()


@router.message(AdminStates.EDIT_DESCRIPTION)
async def edit_description(message: Message, state: FSMContext):
    description = plain_user_text(message.text, message.caption)
    if not description:
        await message.answer(
            "Введите описание текстом или нажмите «Оставить»:",
            reply_markup=edit_keep_keyboard(),
        )
        return
    await state.update_data(description=description)
    await _prompt_edit_featured(message, state)


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
    featured_label = "да" if data.get("is_featured") else "нет"
    text = (
        f"Проверьте изменения:\n\n"
        f"📌 {data['name']}\n"
        f"📅 {format_date_ru(event_date)}, {format_time_ru(event_time)}\n"
        f"📍 {data['location']}\n"
        f"{_price_confirm_line(data)}"
        f"📝 {_description_line(data.get('description'))}\n"
        f"🖼️ Слайдер: {featured_label}\n"
    )
    await state.set_state(AdminStates.EDIT_CONFIRM)
    keyboard = confirm_keyboard("edit")
    if edit:
        await _edit_or_answer(message, text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)
