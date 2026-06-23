from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать событие", callback_data="admin:create")],
            [InlineKeyboardButton(text="Управлять событиями", callback_data="admin:manage")],
        ]
    )


def skip_image_keyboard(*, keep_current: bool = False) -> InlineKeyboardMarkup:
    label = "Оставить текущую" if keep_current else "Пропустить (использовать заглушку)"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data="admin:skip_image")],
        ]
    )


def edit_keep_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить", callback_data="admin:edit:keep")],
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
            [InlineKeyboardButton(text="Участники", callback_data=f"admin:registrations:{event_id}")],
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


def back_to_event_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ К событию", callback_data=f"admin:detail:{event_id}")],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ В меню", callback_data="admin:menu")],
        ]
    )
