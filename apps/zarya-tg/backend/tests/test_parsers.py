from app.bot.parsers import format_guest_count, plain_user_text


def test_format_guest_count_with_limit():
    assert format_guest_count(1, 20) == "Гостей: 1 из 20"


def test_format_guest_count_without_limit():
    assert format_guest_count(3, None) == "Гостей: 3"


def test_plain_user_text_prefers_text_then_caption():
    assert plain_user_text("  дресс-код чёрный  ") == "дресс-код чёрный"
    assert plain_user_text(None, "  текст на фото  ") == "текст на фото"
    assert plain_user_text("  ", None) == ""
    assert plain_user_text(None, None) == ""
