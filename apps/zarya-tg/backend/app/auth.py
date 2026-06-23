import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Validate Telegram WebApp initData per official docs."""
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid init data")

    user_data = parsed.get("user")
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user data")

    return json.loads(user_data)


async def get_current_user(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db),
) -> User:
    settings = get_settings()
    if not settings.bot_token:
        # Dev mode without bot token — use mock user from header
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bot token not configured",
        )

    tg_user = validate_telegram_init_data(x_telegram_init_data, settings.bot_token)
    telegram_id = int(tg_user["id"])

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update username/first_name if changed
        updated = False
        if tg_user.get("username") and user.username != tg_user.get("username"):
            user.username = tg_user.get("username")
            updated = True
        if tg_user.get("first_name") and user.first_name != tg_user.get("first_name"):
            user.first_name = tg_user.get("first_name")
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)

    return user


async def get_optional_user(
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not x_telegram_init_data:
        return None
    return await get_current_user(x_telegram_init_data, db)
