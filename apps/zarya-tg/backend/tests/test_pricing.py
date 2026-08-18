from __future__ import annotations

import pytest

from app.utils.pricing import (
    NARROW_NBSP,
    PricePairError,
    format_event_price,
    normalize_event_price,
    parse_ruble_price,
)


def test_format_event_price_rubles_uses_narrow_nbsp():
    assert format_event_price(100_000, "RUB") == f"1{NARROW_NBSP}000 ₽"
    assert format_event_price(250_000, "rub") == f"2{NARROW_NBSP}500 ₽"
    assert format_event_price(100, "RUB") == "1 ₽"
    assert format_event_price(100_000_000, "RUB") == f"1{NARROW_NBSP}000{NARROW_NBSP}000 ₽"


def test_format_event_price_unset_and_invalid():
    assert format_event_price(None, None) is None
    assert format_event_price(100_000, None) is None
    assert format_event_price(None, "RUB") is None
    assert format_event_price(0, "RUB") is None
    assert format_event_price(-100, "RUB") is None
    assert format_event_price(100_000, "GBP") is None


def test_parse_ruble_price_accepts_spaces_and_symbol():
    assert parse_ruble_price("1000") == 100_000
    assert parse_ruble_price("1 000") == 100_000
    assert parse_ruble_price("1000₽") == 100_000
    assert parse_ruble_price("1\u202f000 руб") == 100_000
    assert parse_ruble_price("  2500  ") == 250_000


def test_parse_ruble_price_rejects_invalid():
    assert parse_ruble_price("0") is None
    assert parse_ruble_price("-10") is None
    assert parse_ruble_price("abc") is None
    assert parse_ruble_price("10.5") is None
    assert parse_ruble_price("10000001") is None
    assert parse_ruble_price("") is None


def test_normalize_event_price_pair():
    assert normalize_event_price(None, None) == (None, None)
    assert normalize_event_price(None, "") == (None, None)
    assert normalize_event_price(100_000, "rub") == (100_000, "RUB")
    with pytest.raises(PricePairError):
        normalize_event_price(100_000, None)
    with pytest.raises(PricePairError):
        normalize_event_price(None, "RUB")
    with pytest.raises(PricePairError):
        normalize_event_price(0, "RUB")
