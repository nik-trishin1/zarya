"""Ops helper: add users to an access group by telegram_id (optional welcome DM).

Usage (from apps/zarya-tg/backend):

  PYTHONPATH=. python -m app.scripts.add_group_members --group core --telegram-ids 123,456

Does not run automatically. Prefer notify=False for dry roster loads if needed.
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from app.database import async_session
from app.services.access_groups import add_user_to_group, get_group_by_slug
from app.services.users import get_user_by_telegram_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _run(group_slug: str, telegram_ids: list[int], notify: bool) -> None:
    async with async_session() as db:
        group = await get_group_by_slug(db, group_slug)
        if group is None:
            raise SystemExit(f"Group not found: {group_slug}")

        for telegram_id in telegram_ids:
            user = await get_user_by_telegram_id(db, telegram_id)
            if user is None:
                logger.warning("Skip telegram_id=%s — user not in DB (must /start the bot first)", telegram_id)
                continue
            membership, created = await add_user_to_group(
                db, user, group, source="admin", notify=notify
            )
            if created:
                logger.info(
                    "Added user_id=%s telegram_id=%s to %s (membership_id=%s, notify=%s)",
                    user.user_id,
                    telegram_id,
                    group.slug,
                    membership.membership_id,
                    notify,
                )
            else:
                logger.info(
                    "Already member user_id=%s telegram_id=%s group=%s",
                    user.user_id,
                    telegram_id,
                    group.slug,
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Add bot users to an access group")
    parser.add_argument("--group", default="core", help="Group slug (default: core)")
    parser.add_argument(
        "--telegram-ids",
        required=True,
        help="Comma-separated Telegram user IDs",
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="Do not send welcome DM (safe for bulk imports)",
    )
    args = parser.parse_args()
    ids = [int(part.strip()) for part in args.telegram_ids.split(",") if part.strip()]
    if not ids:
        raise SystemExit("No telegram ids provided")
    asyncio.run(_run(args.group, ids, notify=not args.no_notify))


if __name__ == "__main__":
    main()
