from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.config import get_settings


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать событие", callback_data="admin:create")],
            [InlineKeyboardButton(text="Управлять событиями", callback_data="admin:manage")],
        ]
    )


def _webapp_url_valid(url: str) -> bool:
    u = url.strip().lower()
    return (
        u.startswith("https://")
        and "localhost" not in u
        and "127.0.0.1" not in u
        and ".internal" not in u
    )


def open_app_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    url = settings.webapp_url.strip()
    if _webapp_url_valid(url):
        button = InlineKeyboardButton(text="🌅 Открыть zarya", web_app=WebAppInfo(url=url))
    else:
        # Fallback when WEBAPP_URL is not set yet — still show a tappable link
        button = InlineKeyboardButton(text="🌅 Открыть zarya", url=url or "https://railway.app")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def skip_image_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить (использовать заглушку)", callback_data="admin:skip_image")],
        ]
    )


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin:{action}:confirm"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="admin:cancel"),
            ],
        ]
    )


def event_manage_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Редактировать", callback_data=f"admin:edit:{event_id}")],
            [InlineKeyboardButton(text="Удалить", callback_data=f"admin:delete:{event_id}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:manage")],
        ]
    )


def delete_confirm_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, удалить", callback_data=f"admin:delete_confirm:{event_id}"),
                InlineKeyboardButton(text="Отмена", callback_data=f"admin:detail:{event_id}"),
            ],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ В меню", callback_data="admin:menu")],
        ]
    )
