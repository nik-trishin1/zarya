from __future__ import annotations

import re
import secrets
import string

SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$|^[a-zA-Z0-9]$")
_ALPHABET = string.ascii_lowercase + string.digits


def is_valid_slug(slug: str) -> bool:
    return bool(SLUG_PATTERN.match(slug))


def generate_slug(length: int = 8) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
