from __future__ import annotations

import logging
from datetime import date, time

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.bot.keyboards import (
    approval_mode_keyboard,
    audience_keyboard,
    edit_keep_keyboard,
    featured_keyboard,
    skip_image_keyboard,
    skip_price_keyboard,
)
from app.bot.parsers import format_date_ru, format_time_ru
from app.bot.states import AdminStates
from app.config import get_settings
from app.database import async_session
from app.services.access_groups import list_access_groups
from app.services.users import get_or_create_user
from app.utils.pricing import format_event_price
from app.services.storage import (
    MAX_FILE_SIZE,
    save_cover_image_bytes,
)

logger = logging.getLogger(__name__)
router = Router()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


_COVER_RETRY_HINT = (
    "\n\nЗагрузите другое изображение (JPEG или PNG, до 5 МБ) или нажмите «Пропустить»."
)
_PRICE_PROMPT = "Введите стоимость в рублях (например 1000) или нажмите «Без стоимости»"
_PRICE_RETRY = (
    "Не удалось распознать сумму. Введите целое число (например 1000) "
    "или нажмите «Без стоимости»:"
)


def _price_label_from_data(data: dict) -> str | None:
    return format_event_price(data.get("price_amount_minor"), data.get("price_currency"))


def _price_confirm_line(data: dict) -> str:
    label = _price_label_from_data(data)
    return f"{label}\n" if label else ""


def _event_price_line(event) -> str:
    label = format_event_price(
        getattr(event, "price_amount_minor", None),
        getattr(event, "price_currency", None),
    )
    return f"{label}\n" if label else ""


def _description_line(description: str | None) -> str:
    text = (description or "").strip()
    return text if text else "—"


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


async def _goto_edit_price(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    current = _price_label_from_data(data) or "не указана"
    await _send_edit_prompt(
        message,
        state,
        text=f"Текущая стоимость: {current}\n\n{_PRICE_PROMPT}",
        next_state=AdminStates.EDIT_PRICE,
        reply_markup=skip_price_keyboard(keep_current=True),
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


async def _prompt_create_approval(message: Message, state: FSMContext, *, edit: bool) -> None:
    await state.set_state(AdminStates.CREATE_APPROVAL)
    text = "Как записывать?"
    markup = approval_mode_keyboard()
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def _prompt_create_audience(message: Message, state: FSMContext, *, edit: bool) -> None:
    async with async_session() as db:
        groups = await list_access_groups(db)
    await state.set_state(AdminStates.CREATE_AUDIENCE)
    text = "Для кого это событие?"
    markup = audience_keyboard(groups)
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def _prompt_create_featured(message: Message, state: FSMContext, *, edit: bool) -> None:
    await state.set_state(AdminStates.CREATE_FEATURED)
    text = "Показать в слайдере на главной?"
    markup = featured_keyboard()
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


async def _prompt_edit_featured(message: Message, state: FSMContext, *, edit: bool = False) -> None:
    data = await state.get_data()
    current = "да" if data.get("is_featured") else "нет"
    await state.set_state(AdminStates.EDIT_FEATURED)
    text = f"Показать в слайдере на главной?\nСейчас: {current}"
    markup = featured_keyboard(keep_current=True)
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


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
