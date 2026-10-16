from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from app.config import Settings, get_settings


def tokens_match(provided: str | None, expected: str) -> bool:
    if not provided or not expected:
        return False
    return secrets.compare_digest(provided, expected)


def extract_admin_token(
    request: Request,
    settings: Settings,
    *,
    x_admin_token: str | None = None,
    form_token: str | None = None,
) -> str | None:
    if x_admin_token and tokens_match(x_admin_token, settings.admin_token):
        return x_admin_token
    if form_token and tokens_match(form_token, settings.admin_token):
        return form_token
    cookie_token = request.cookies.get(settings.cookie_name)
    if cookie_token and tokens_match(cookie_token, settings.admin_token):
        return cookie_token
    return None


async def require_admin(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_token: Annotated[str | None, Header()] = None,
) -> str:
    token = extract_admin_token(request, settings, x_admin_token=x_admin_token)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return token
