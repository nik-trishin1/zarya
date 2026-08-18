from __future__ import annotations

NARROW_NBSP = "\u202f"
MAX_RUBLES = 10_000_000
DEFAULT_CURRENCY = "RUB"

_CURRENCY_SYMBOLS = {
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
}

_STRIP_TOKENS = ("рублей", "рубля", "руб.", "руб", "₽")
_SPACE_CHARS = " \t\u00a0\u202f\u2009"


class PricePairError(ValueError):
    """Raised when amount and currency are not a valid pair."""


def parse_ruble_price(text: str) -> int | None:
    """Parse whole-ruble admin input into minor units, or None if invalid."""
    raw = text.strip().lower().replace("ё", "е")
    for token in _STRIP_TOKENS:
        raw = raw.replace(token, "")
    raw = "".join(ch for ch in raw if ch not in _SPACE_CHARS)
    if not raw.isdigit():
        return None
    rubles = int(raw)
    if rubles < 1 or rubles > MAX_RUBLES:
        return None
    return rubles * 100


def format_event_price(amount_minor: int | None, currency: str | None) -> str | None:
    """Canonical display, e.g. 100000 + RUB → '1 000 ₽'. None when unset."""
    if amount_minor is None or currency is None:
        return None
    if amount_minor <= 0:
        return None
    code = currency.strip().upper()
    symbol = _CURRENCY_SYMBOLS.get(code)
    if symbol is None:
        return None
    major, remainder = divmod(amount_minor, 100)
    grouped = _group_int(major)
    number = f"{grouped}.{remainder:02d}" if remainder else grouped
    return f"{number} {symbol}"


def normalize_event_price(
    amount_minor: int | None,
    currency: str | None,
) -> tuple[int | None, str | None]:
    """Both null, or both set with amount > 0 and a 3-letter ISO code."""
    currency_empty = currency is None or not str(currency).strip()
    if amount_minor is None and currency_empty:
        return None, None
    if amount_minor is None or currency_empty:
        raise PricePairError("price amount and currency must be set together")
    if amount_minor <= 0:
        raise PricePairError("price amount must be positive")
    code = str(currency).strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise PricePairError("invalid currency code")
    return amount_minor, code


def _group_int(value: int) -> str:
    digits = str(abs(value))
    parts: list[str] = []
    while digits:
        parts.append(digits[-3:])
        digits = digits[:-3]
    grouped = NARROW_NBSP.join(reversed(parts))
    if value < 0:
        return f"-{grouped}"
    return grouped
