from app.bot.parsers import format_guest_count


def test_format_guest_count_with_limit():
    assert format_guest_count(1, 20) == "Гостей: 1 из 20"


def test_format_guest_count_without_limit():
    assert format_guest_count(3, None) == "Гостей: 3"
