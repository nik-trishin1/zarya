from __future__ import annotations

import base64
import hashlib
import hmac
import time


def create_calendar_token(user_id: int, event_id: int, secret: str, ttl_seconds: int = 300) -> str:
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{user_id}:{event_id}:{expires_at}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def verify_calendar_token(token: str, event_id: int, secret: str) -> int | None:
    try:
        padding = "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + padding).decode()
        user_id_str, token_event_id_str, expires_at_str, signature = raw.rsplit(":", 3)
        payload = f"{user_id_str}:{token_event_id_str}:{expires_at_str}"
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(signature, expected):
            return None
        if int(token_event_id_str) != event_id:
            return None
        if int(expires_at_str) < int(time.time()):
            return None
        return int(user_id_str)
    except (ValueError, UnicodeDecodeError):
        return None
