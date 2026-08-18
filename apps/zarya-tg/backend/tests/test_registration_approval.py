from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from sqlalchemy import select

from app.bot.participants import format_participants_message
from app.database import async_session, engine, Base
from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.models.user import User
from app.services.admin_notifications import (
    build_admin_application_message,
    build_user_approval_message,
    build_user_rejection_message,
)
from app.services.events import (
    approve_registration,
    cancel_registration,
    get_event_detail,
    get_event_registered_users,
    get_upcoming_events,
    mark_maybe,
    register_user,
    reject_registration,
    update_party_size,
)
from app.services.users import get_or_create_user


@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


def _future_event(**kwargs) -> Event:
    defaults = dict(
        name="Фестиваль",
        description="",
        date=date.today() + timedelta(days=10),
        time=time(19, 0),
        location="Москва",
        requires_approval=True,
    )
    defaults.update(kwargs)
    return Event(**defaults)


@pytest.mark.asyncio
async def test_apply_on_approval_event_is_pending_without_seat():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_001, username="guest", first_name="Guest")
        event = _future_event(max_participants=5)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        attendance = await register_user(db, user, event.event_id, party_size=2)
        assert attendance.is_pending is True
        assert attendance.is_registered is False
        assert attendance.is_maybe is False
        assert attendance.registration_count == 0

        row = (
            await db.execute(
                select(Registration).where(
                    Registration.user_id == user.user_id,
                    Registration.event_id == event.event_id,
                )
            )
        ).scalar_one()
        assert row.status == RegistrationStatus.PENDING.value
        assert row.party_size == 2


@pytest.mark.asyncio
async def test_open_event_still_registers_active():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_002, username="open", first_name="Open")
        event = _future_event(requires_approval=False)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        attendance = await register_user(db, user, event.event_id)
        assert attendance.is_registered is True
        assert attendance.is_pending is False
        assert attendance.registration_count == 1


@pytest.mark.asyncio
async def test_already_pending_is_conflict():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_003, username="dup", first_name="Dup")
        event = _future_event()
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()
        await register_user(db, user, event.event_id)
        with pytest.raises(ValueError, match="Already pending"):
            await register_user(db, user, event.event_id)


@pytest.mark.asyncio
async def test_approve_occupies_seats_and_reject_cancels():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_004, username="ok", first_name="Ok")
        other = await get_or_create_user(db, telegram_id=930_005, username="no", first_name="No")
        event = _future_event(max_participants=3)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        u1 = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()
        u2 = (await db.execute(select(User).where(User.user_id == other.user_id))).scalar_one()

        await register_user(db, u1, event.event_id, party_size=2)
        await register_user(db, u2, event.event_id, party_size=1)

        approved = await approve_registration(db, event.event_id, u1.user_id)
        assert approved.is_registered is True
        assert approved.registration_count == 2
        assert approved.party_size == 2

        rejected = await reject_registration(db, event.event_id, u2.user_id)
        assert rejected.is_pending is False
        assert rejected.is_registered is False
        assert rejected.registration_count == 2

        row = (
            await db.execute(
                select(Registration).where(
                    Registration.user_id == u2.user_id,
                    Registration.event_id == event.event_id,
                )
            )
        ).scalar_one()
        assert row.status == RegistrationStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_reapply_after_cancel_is_pending_again():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_006, username="re", first_name="Re")
        event = _future_event()
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        await register_user(db, user, event.event_id)
        await approve_registration(db, event.event_id, user.user_id)
        await cancel_registration(db, user, event.event_id)
        again = await register_user(db, user, event.event_id)
        assert again.is_pending is True
        assert again.is_registered is False


@pytest.mark.asyncio
async def test_approve_when_full_keeps_pending():
    async with async_session() as db:
        first = await get_or_create_user(db, telegram_id=930_007, username="a", first_name="A")
        second = await get_or_create_user(db, telegram_id=930_008, username="b", first_name="B")
        event = _future_event(max_participants=1)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        u1 = (await db.execute(select(User).where(User.user_id == first.user_id))).scalar_one()
        u2 = (await db.execute(select(User).where(User.user_id == second.user_id))).scalar_one()

        await register_user(db, u1, event.event_id)
        await approve_registration(db, event.event_id, u1.user_id)
        with pytest.raises(ValueError, match="Event full"):
            await register_user(db, u2, event.event_id)

        # leftover pending from before fill: create by temporarily raising capacity then filling
        event.max_participants = 2
        await db.commit()
        await register_user(db, u2, event.event_id)
        event.max_participants = 1
        await db.commit()
        with pytest.raises(ValueError, match="Event full"):
            await approve_registration(db, event.event_id, u2.user_id)
        detail = await get_event_detail(db, event.event_id, u2)
        assert detail is not None
        assert detail.is_pending is True


@pytest.mark.asyncio
async def test_my_registrations_include_pending_not_maybe():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_009, username="mine", first_name="Mine")
        pending_event = _future_event(name="Pending gig")
        maybe_event = _future_event(name="Maybe gig", requires_approval=False)
        db.add_all([pending_event, maybe_event])
        await db.commit()
        await db.refresh(pending_event)
        await db.refresh(maybe_event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        await register_user(db, user, pending_event.event_id)
        await mark_maybe(db, user, maybe_event.event_id)

        mine = await get_upcoming_events(db, user=user, registered_only=True)
        names = {row.event.name for row in mine}
        assert "Pending gig" in names
        assert "Maybe gig" not in names
        pending_row = next(row for row in mine if row.event.name == "Pending gig")
        assert pending_row.is_pending is True


@pytest.mark.asyncio
async def test_broadcast_recipients_exclude_pending():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_010, username="bc", first_name="Bc")
        event = _future_event()
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()
        await register_user(db, user, event.event_id)
        recipients = await get_event_registered_users(db, event.event_id)
        assert recipients == []
        await approve_registration(db, event.event_id, user.user_id)
        recipients = await get_event_registered_users(db, event.event_id)
        assert [u.user_id for u in recipients] == [user.user_id]


@pytest.mark.asyncio
async def test_maybe_then_apply_clears_maybe_and_patch_party_size_active_only():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_011, username="mb", first_name="Mb")
        event = _future_event()
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        await mark_maybe(db, user, event.event_id)
        applied = await register_user(db, user, event.event_id, party_size=1)
        assert applied.is_pending is True
        assert applied.is_maybe is False
        with pytest.raises(ValueError, match="Not registered"):
            await update_party_size(db, user, event.event_id, 2)
        with pytest.raises(ValueError, match="Already pending"):
            await mark_maybe(db, user, event.event_id)


@pytest.mark.asyncio
async def test_maybe_apply_on_full_approval_event_keeps_maybe():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_013, username="fullmb", first_name="Full")
        other = await get_or_create_user(db, telegram_id=930_014, username="seat", first_name="Seat")
        event = _future_event(max_participants=1)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()
        seater = (await db.execute(select(User).where(User.user_id == other.user_id))).scalar_one()

        await mark_maybe(db, user, event.event_id)
        event.requires_approval = False
        await db.commit()
        await register_user(db, seater, event.event_id, party_size=1)
        event.requires_approval = True
        await db.commit()

        with pytest.raises(ValueError, match="Event full"):
            await register_user(db, user, event.event_id, party_size=1)
        detail = await get_event_detail(db, event.event_id, user)
        assert detail is not None
        assert detail.is_maybe is True
        assert detail.is_pending is False


@pytest.mark.asyncio
async def test_pending_acl_escape_hatch_like_maybe():
    from sqlalchemy import delete

    from app.models.group_membership import GroupMembership
    from app.schema_updates import CORE_GROUP_SLUG
    from app.services.access_groups import add_user_to_group, get_group_by_slug

    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        guest = await get_or_create_user(db, telegram_id=930_015, username="out", first_name="Out")
        await add_user_to_group(db, guest, group, notify=False)
        event = _future_event(audience_group_id=group.group_id)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()

        attendance = await register_user(db, user, event.event_id)
        assert attendance.is_pending is True

        await db.execute(
            delete(GroupMembership).where(
                GroupMembership.user_id == user.user_id,
                GroupMembership.group_id == group.group_id,
            )
        )
        await db.commit()

        detail = await get_event_detail(db, event.event_id, user)
        assert detail is not None
        assert detail.is_pending is True


@pytest.mark.asyncio
async def test_idempotent_approve_and_reject():
    async with async_session() as db:
        guest = await get_or_create_user(db, telegram_id=930_012, username="id", first_name="Id")
        event = _future_event()
        db.add(event)
        await db.commit()
        await db.refresh(event)
        user = (await db.execute(select(User).where(User.user_id == guest.user_id))).scalar_one()
        await register_user(db, user, event.event_id)
        await approve_registration(db, event.event_id, user.user_id)
        with pytest.raises(ValueError, match="Already registered"):
            await approve_registration(db, event.event_id, user.user_id)
        with pytest.raises(ValueError, match="Already registered"):
            await reject_registration(db, event.event_id, user.user_id)


def test_application_copy():
    event = Event(
        event_id=1,
        name="Фест",
        description="",
        date=date(2026, 6, 28),
        time=time(19, 0),
        location="Москва",
    )
    user = User(user_id=1, telegram_id=100, username="anna", first_name="Anna")
    message = build_admin_application_message(user, event, 0, party_size=2)
    assert "подал(а) заявку на *Фест*" in message
    assert "Гостей в заявке: 2" in message
    assert build_user_approval_message(event) == (
        "Ваше участие на Фест · Вс, 28 июня, 19:00 подтверждено!"
    )
    assert build_user_rejection_message(event) == "Заявку на Фест не подтвердили."


def test_participants_pending_block():
    pending = User(user_id=2, telegram_id=200, username="ann", first_name="Анна")
    going = User(user_id=3, telegram_id=300, username="bob", first_name="Боб")
    message = format_participants_message(
        "Фест",
        [(going, 1)],
        pending_users=[(pending, 1)],
    )
    assert "Заявки:" in message
    assert "1. Анна @ann — на рассмотрении" in message
    assert "1. Боб @bob" in message
    assert message.endswith("Всего: 1")
