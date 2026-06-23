from __future__ import annotations

import io
import logging
from datetime import date, time

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    admin_menu_keyboard,
    back_to_menu_keyboard,
    confirm_keyboard,
    delete_confirm_keyboard,
    event_manage_keyboard,
    skip_image_keyboard,
)
from app.bot.parsers import format_date_ru, format_time_ru, parse_date, parse_time
from app.bot.states import AdminStates
from app.config import get_settings
from app.database import async_session
from app.services.events import (
    create_event,
    delete_event,
    get_all_events_admin,
    get_event_by_id,
    get_or_create_admin_user,
    update_event,
)
from app.services.storage import MAX_FILE_SIZE, image_too_large_message, save_cover_image_bytes

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


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 🌅\n"
        "Мы ждем тебя на наших скорых встречах.\n"
        "Нажми кнопку меню, чтобы посмотреть предстоящие события!",
    )


@router.message(Command("myid"))
async def cmd_myid(message: Message):
    user = message.from_user
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
    cover_url = await _save_cover_from_message(message, buffer.getvalue(), doc.file_name or "cover.jpg")
    if cover_url is None:
        return
    await state.update_data(cover_image_url=cover_url)
    await show_create_confirm(message, state)


@router.callback_query(F.data == "admin:skip_image", AdminStates.CREATE_IMAGE)
async def create_skip_image(callback: CallbackQuery, state: FSMContext):
    settings = get_settings()
    default_url = f"{settings.api_base_url.rstrip('/')}/static/default-cover.svg"
    await state.update_data(cover_image_url=default_url)
    await show_create_confirm(callback.message, state, edit=True)
    await callback.answer()


async def show_create_confirm(message: Message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    event_date = date.fromisoformat(data["event_date"])
    event_time = time.fromisoformat(data["event_time"])
    text = (
        f"Проверьте данные:\n\n"
        f"📌 {data['name']}\n"
        f"📅 {format_date_ru(event_date)}, {format_time_ru(event_time)}\n"
        f"📍 {data['location']}\n"
        f"📝 {data.get('description', '')}\n"
    )
    await state.set_state(AdminStates.CREATE_CONFIRM)
    if edit:
        await message.edit_text(text, reply_markup=confirm_keyboard("create"))
    else:
        await message.answer(text, reply_markup=confirm_keyboard("create"))


@router.callback_query(F.data == "admin:create:confirm")
async def create_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as db:
        admin_user = await get_or_create_admin_user(
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
            cover_image_url=data.get("cover_image_url"),
            admin_user=admin_user,
        )

    event_date = date.fromisoformat(data["event_date"])
    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text(
        f"Событие создано: {event.name} на {format_date_ru(event_date)} ✅",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


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
        label = f"{event.name} | {format_date_ru(event.date)} | {reg_count} чел."
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
        f"Зарегистрировано: {reg_count} человек\n\n"
        f"{event.description}"
    )
    await state.set_state(AdminStates.MANAGE_DETAIL)
    await state.update_data(event_id=event_id)
    await callback.message.edit_text(text, reply_markup=event_manage_keyboard(event_id))
    await callback.answer()


# --- Edit event ---

@router.callback_query(F.data.startswith("admin:edit:"))
async def admin_edit_start(callback: CallbackQuery, state: FSMContext):
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
        cover_image_url=event.cover_image_url,
        edit_mode=True,
    )
    await state.set_state(AdminStates.EDIT_NAME)
    await callback.message.edit_text(
        f"Текущее название: {event.name}\n\nВведите новое название или отправьте «-» чтобы оставить:"
    )
    await callback.answer()


@router.message(AdminStates.EDIT_NAME)
async def edit_name(message: Message, state: FSMContext):
    if message.text and message.text.strip() != "-":
        await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.EDIT_DATE)
    data = await state.get_data()
    await message.answer(
        f"Текущая дата: {format_date_ru(date.fromisoformat(data['event_date']))}\n"
        "Введите новую дату или «-» чтобы оставить:"
    )


@router.message(AdminStates.EDIT_DATE)
async def edit_date(message: Message, state: FSMContext):
    if message.text and message.text.strip() != "-":
        parsed = parse_date(message.text)
        if parsed is None:
            await message.answer("Не удалось распознать дату. Формат: ДД.ММ.ГГГГ")
            return
        await state.update_data(event_date=parsed.isoformat())
    await state.set_state(AdminStates.EDIT_TIME)
    data = await state.get_data()
    await message.answer(
        f"Текущее время: {format_time_ru(time.fromisoformat(data['event_time']))}\n"
        "Введите новое время или «-» чтобы оставить:"
    )


@router.message(AdminStates.EDIT_TIME)
async def edit_time(message: Message, state: FSMContext):
    if message.text and message.text.strip() != "-":
        parsed = parse_time(message.text)
        if parsed is None:
            await message.answer("Не удалось распознать время. Формат: ЧЧ:ММ")
            return
        await state.update_data(event_time=parsed.isoformat())
    await state.set_state(AdminStates.EDIT_LOCATION)
    data = await state.get_data()
    await message.answer(f"Текущее место: {data['location']}\nВведите новое место или «-» чтобы оставить:")


@router.message(AdminStates.EDIT_LOCATION)
async def edit_location(message: Message, state: FSMContext):
    if message.text and message.text.strip() != "-":
        await state.update_data(location=message.text.strip())
    await state.set_state(AdminStates.EDIT_DESCRIPTION)
    data = await state.get_data()
    await message.answer(
        f"Текущее описание: {data.get('description', '')}\n"
        "Введите новое описание или «-» чтобы оставить:"
    )


@router.message(AdminStates.EDIT_DESCRIPTION)
async def edit_description(message: Message, state: FSMContext):
    if message.text and message.text.strip() != "-":
        await state.update_data(description=message.text.strip())
    await state.set_state(AdminStates.EDIT_IMAGE)
    await message.answer(
        "Загрузите новую обложку (JPEG или PNG, до 5 МБ) или пропустите (оставить текущую):",
        reply_markup=skip_image_keyboard(),
    )


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
    cover_url = await _save_cover_from_message(message, buffer.getvalue(), doc.file_name or "cover.jpg")
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
    if edit:
        await message.edit_text(text, reply_markup=confirm_keyboard("edit"))
    else:
        await message.answer(text, reply_markup=confirm_keyboard("edit"))


@router.callback_query(F.data == "admin:edit:confirm")
async def edit_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event_id = data["event_id"]
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
            cover_image_url=data.get("cover_image_url"),
        )

    await state.clear()
    await state.set_state(AdminStates.MENU)
    await callback.message.edit_text(
        f"Событие обновлено: {data['name']} ✅",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


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
