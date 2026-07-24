from __future__ import annotations

import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.access_group import AccessGroup
from app.models.event import Event
from app.models.group_membership import GroupMembership
from app.models.user import User
from app.services.telegram_delivery import deliver_bot_message
from app.schema_updates import CORE_GROUP_NAME, CORE_GROUP_SLUG

logger = logging.getLogger(__name__)

WELCOME_TEMPLATE = "Привет! Теперь тебе доступны события группы *{name}*. До встречи!"


def is_admin_telegram_id(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


def event_is_public(event: Event) -> bool:
    return event.audience_group_id is None


def event_allows_plus_one(event: Event) -> bool:
    return event_is_public(event)


def event_allows_sharing(event: Event) -> bool:
    return event_is_public(event)


async def list_access_groups(db: AsyncSession) -> list[AccessGroup]:
    result = await db.execute(select(AccessGroup).order_by(AccessGroup.group_id.asc()))
    return list(result.scalars().all())


async def get_group_by_id(db: AsyncSession, group_id: int) -> AccessGroup | None:
    result = await db.execute(select(AccessGroup).where(AccessGroup.group_id == group_id))
    return result.scalar_one_or_none()


async def get_group_by_slug(db: AsyncSession, slug: str) -> AccessGroup | None:
    result = await db.execute(select(AccessGroup).where(AccessGroup.slug == slug))
    return result.scalar_one_or_none()


async def ensure_core_group(db: AsyncSession) -> AccessGroup:
    group = await get_group_by_slug(db, CORE_GROUP_SLUG)
    if group is not None:
        return group
    group = AccessGroup(slug=CORE_GROUP_SLUG, name=CORE_GROUP_NAME)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def user_group_ids(db: AsyncSession, user_id: int) -> set[int]:
    result = await db.execute(
        select(GroupMembership.group_id).where(GroupMembership.user_id == user_id)
    )
    return {int(group_id) for group_id in result.scalars().all()}


async def is_group_member(db: AsyncSession, user_id: int, group_id: int) -> bool:
    result = await db.execute(
        select(GroupMembership.membership_id).where(
            GroupMembership.user_id == user_id,
            GroupMembership.group_id == group_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def can_view_event(db: AsyncSession, event: Event, user: User | None) -> bool:
    if event_is_public(event):
        return True
    if user is None:
        return False
    if is_admin_telegram_id(user.telegram_id):
        return True
    assert event.audience_group_id is not None
    return await is_group_member(db, user.user_id, event.audience_group_id)


async def can_register_for_event(db: AsyncSession, event: Event, user: User) -> bool:
    return await can_view_event(db, event, user)


async def get_group_members(db: AsyncSession, group_id: int) -> list[User]:
    result = await db.execute(
        select(User)
        .join(GroupMembership, GroupMembership.user_id == User.user_id)
        .where(GroupMembership.group_id == group_id)
        .order_by(User.user_id.asc())
    )
    return list(result.scalars().all())


async def count_group_members(db: AsyncSession, group_id: int) -> int:
    members = await get_group_members(db, group_id)
    return len(members)


async def get_announcement_recipients(
    db: AsyncSession,
    audience_group_id: int | None,
) -> list[User]:
    """Recipients for new-event announce / audience-sized previews."""
    if audience_group_id is None:
        from app.services.users import get_all_users

        return await get_all_users(db)
    return await get_group_members(db, audience_group_id)


def build_group_welcome_message(group_name: str) -> str:
    return WELCOME_TEMPLATE.format(name=group_name)


async def send_group_welcome(user: User, group: AccessGroup) -> bool:
    settings = get_settings()
    if not settings.bot_token_configured:
        return False
    bot = Bot(token=settings.bot_token.strip())
    try:
        outcome = await deliver_bot_message(
            bot,
            None,
            user.telegram_id,
            build_group_welcome_message(group.name),
            user=user,
            context=f"group_welcome group_id={group.group_id}",
            parse_mode="Markdown",
        )
        return outcome.value == "sent"
    finally:
        await bot.session.close()


async def add_user_to_group(
    db: AsyncSession,
    user: User,
    group: AccessGroup,
    *,
    source: str = "admin",
    notify: bool = True,
) -> tuple[GroupMembership, bool]:
    """Add membership. Returns (membership, created). Welcome only when created and notify=True."""
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.user_id == user.user_id,
            GroupMembership.group_id == group.group_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing, False

    membership = GroupMembership(
        user_id=user.user_id,
        group_id=group.group_id,
        source=source,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    if notify:
        try:
            await send_group_welcome(user, group)
        except Exception:
            logger.exception(
                "Failed to send group welcome user_id=%s group_id=%s",
                user.user_id,
                group.group_id,
            )

    return membership, True


def audience_label(group: AccessGroup | None) -> str:
    if group is None:
        return "Все участники"
    return group.name
