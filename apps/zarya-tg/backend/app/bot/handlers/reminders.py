from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select

from app.database import async_session
from app.models.registration import Registration, RegistrationStatus
from app.services.admin_notifications import (
    notify_admins_application,
    notify_admins_registration_change,
)
from app.services.events import (
    cancel_registration,
    clear_maybe_registration,
    get_event_by_id,
    register_user,
)
from app.services.users import get_or_create_user

router = Router()


@router.callback_query(F.data.regexp(r"^reminder:cancel:\d+$"))
async def reminder_cancel_registration(callback: CallbackQuery):
    if callback.from_user is None:
        await callback.answer()
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        user = await get_or_create_user(
            db,
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.first_name,
        )
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        try:
            attendance = await cancel_registration(db, user, event_id)
            event = attendance.event
        except ValueError as e:
            if str(e) == "Not registered":
                await callback.answer("Вы не зарегистрированы на это событие", show_alert=True)
                return
            raise

    await callback.answer(f"Вы отменили регистрацию на «{event.name}»", show_alert=True)


@router.callback_query(F.data.regexp(r"^maybe:going:\d+$"))
async def maybe_ping_going(callback: CallbackQuery):
    if callback.from_user is None:
        await callback.answer()
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        user = await get_or_create_user(
            db,
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.first_name,
        )
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        try:
            attendance = await register_user(db, user, event_id, party_size=1)
            event = attendance.event
        except ValueError as e:
            code = str(e)
            if code == "Already registered":
                await callback.answer("Вы уже зарегистрированы", show_alert=True)
                return
            if code == "Already pending":
                await callback.answer("Заявка уже на рассмотрении", show_alert=True)
                return
            if code == "Event full":
                await callback.answer("Мест нет", show_alert=True)
                return
            if code == "Event past":
                await callback.answer("Событие уже прошло", show_alert=True)
                return
            if code == "Event not found":
                await callback.answer("Событие не найдено", show_alert=True)
                return
            raise

    if attendance.is_pending:
        await notify_admins_application(
            user,
            attendance.event,
            attendance.registration_count,
            party_size=1,
        )
    elif attendance.is_registered:
        await notify_admins_registration_change(
            user,
            attendance.event,
            attendance.registration_count,
            registered=True,
            party_size=attendance.party_size or 1,
        )

    await callback.answer(
        "Заявка отправлена. Ждём подтверждения."
        if attendance.is_pending
        else f"Вы зарегистрированы на «{event.name}»",
        show_alert=True,
    )


@router.callback_query(F.data.regexp(r"^maybe:decline:\d+$"))
async def maybe_ping_decline(callback: CallbackQuery):
    if callback.from_user is None:
        await callback.answer()
        return

    event_id = int(callback.data.split(":")[-1])
    async with async_session() as db:
        user = await get_or_create_user(
            db,
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.first_name,
        )
        event = await get_event_by_id(db, event_id)
        if event is None:
            await callback.answer("Событие не найдено", show_alert=True)
            return
        try:
            attendance = await clear_maybe_registration(db, user, event_id)
            event = attendance.event
        except ValueError as e:
            if str(e) == "Not maybe":
                active = await db.execute(
                    select(Registration).where(
                        Registration.user_id == user.user_id,
                        Registration.event_id == event_id,
                        Registration.status == RegistrationStatus.ACTIVE.value,
                    )
                )
                if active.scalar_one_or_none() is not None:
                    await callback.answer(
                        "Вы уже зарегистрированы — отмените регистрацию в приложении",
                        show_alert=True,
                    )
                    return
                await callback.answer("Отметка уже снята", show_alert=True)
                return
            raise

    await callback.answer(f"Отметили, что не сможете на «{event.name}»", show_alert=True)
