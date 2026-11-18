from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

from .common import is_admin
from app.bot.keyboards import back_to_event_keyboard, pending_list_keyboard
from app.bot.participants import format_participants_message
from app.database import async_session
from app.models.user import User as DbUser
from app.services.admin_notifications import notify_user_application_decision
from app.services.events import (
    approve_registration,
    get_event_by_id,
    get_event_maybe_users,
    get_event_pending_users,
    get_event_registration_parties,
    reject_registration,
)

router = Router()


async def _render_participants_list(
    callback: CallbackQuery, state: FSMContext, event_id: int
) -> None:
    async with async_session() as db:
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        parties = await get_event_registration_parties(db, event_id)
        maybe_users = await get_event_maybe_users(db, event_id)
        pending_users = await get_event_pending_users(db, event_id)
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


@router.callback_query(F.data.regexp(r"^admin:approve:\d+:\d+$"))
async def admin_approve_application(callback: CallbackQuery, state: FSMContext):
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    parts = callback.data.split(":")
    event_id = int(parts[2])
    applicant_id = int(parts[3])
    async with async_session() as db:
        try:
            attendance = await approve_registration(db, event_id, applicant_id)
        except ValueError as e:
            code = str(e)
            if code == "Already registered":
                await callback.answer("Уже подтверждено", show_alert=True)
                return
            if code == "Not pending":
                await callback.answer("Заявка уже снята", show_alert=True)
                return
            if code == "Event full":
                await callback.answer("Недостаточно мест", show_alert=True)
                return
            if code in {"Event not found", "User not found"}:
                await callback.answer("Событие не найдено", show_alert=True)
                return
            raise
        result = await db.execute(select(DbUser).where(DbUser.user_id == applicant_id))
        applicant_user = result.scalar_one_or_none()
        event = attendance.event

    if applicant_user is not None:
        await notify_user_application_decision(applicant_user, event, accepted=True)
    await callback.answer("Заявка принята")
    msg_text = callback.message.text or "" if callback.message else ""
    if msg_text.startswith("Участники:"):
        await _render_participants_list(callback, state, event_id)
    elif callback.message:
        try:
            await callback.message.edit_text(msg_text + "\n\n✅ Принято")
        except TelegramBadRequest:
            pass


@router.callback_query(F.data.regexp(r"^admin:reject:\d+:\d+$"))
async def admin_reject_application(callback: CallbackQuery, state: FSMContext):
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    parts = callback.data.split(":")
    event_id = int(parts[2])
    applicant_id = int(parts[3])
    async with async_session() as db:
        try:
            attendance = await reject_registration(db, event_id, applicant_id)
        except ValueError as e:
            code = str(e)
            if code == "Already registered":
                await callback.answer("Уже подтверждено", show_alert=True)
                return
            if code == "Not pending":
                await callback.answer("Заявка уже снята", show_alert=True)
                return
            if code in {"Event not found", "User not found"}:
                await callback.answer("Событие не найдено", show_alert=True)
                return
            raise
        result = await db.execute(select(DbUser).where(DbUser.user_id == applicant_id))
        applicant_user = result.scalar_one_or_none()
        event = attendance.event

    if applicant_user is not None:
        await notify_user_application_decision(applicant_user, event, accepted=False)
    await callback.answer("Заявка отклонена")
    msg_text = callback.message.text or "" if callback.message else ""
    if msg_text.startswith("Участники:"):
        await _render_participants_list(callback, state, event_id)
    elif callback.message:
        try:
            await callback.message.edit_text(msg_text + "\n\n❌ Отклонено")
        except TelegramBadRequest:
            pass
