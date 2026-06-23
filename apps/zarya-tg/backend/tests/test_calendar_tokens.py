from __future__ import annotations

import base64
import hashlib
import hmac
import time

from app.utils.calendar_tokens import create_calendar_token, verify_calendar_token


def test_calendar_token_roundtrip():
    secret = "test-secret"
    token = create_calendar_token(user_id=42, event_id=7, secret=secret, ttl_seconds=300)
    assert verify_calendar_token(token, event_id=7, secret=secret) == 42


def test_calendar_token_wrong_event():
    secret = "test-secret"
    token = create_calendar_token(user_id=42, event_id=7, secret=secret)
    assert verify_calendar_token(token, event_id=99, secret=secret) is None


def test_calendar_token_expired():
    secret = "test-secret"
    token = create_calendar_token(user_id=42, event_id=7, secret=secret, ttl_seconds=-1)
    assert verify_calendar_token(token, event_id=7, secret=secret) is None
