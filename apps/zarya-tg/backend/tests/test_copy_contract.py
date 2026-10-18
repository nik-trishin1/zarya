"""Pin user-facing copy to the ADR, not to whatever the last edit rendered.

ADR-012 guest line and the description step are the production regressions
from 2026-10-18. See docs/postmortems/2026-10-18-incorrect-event-copy.md.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from app.bot.handlers import create_description, edit_description
from app.bot.parsers import format_guest_count
from app.bot.states import AdminStates

ZARYA_TG = Path(__file__).resolve().parents[2]
FRONTEND_SRC = ZARYA_TG / "frontend" / "src"
FORMAT_TS = FRONTEND_SRC / "utils" / "format.ts"


def test_frontend_guest_line_matches_adr_012():
    source = FORMAT_TS.read_text(encoding="utf-8")
    assert "return `Гостей: ${registrationCount} из ${maxParticipants}`;" in source
    assert "return `Гостей: ${registrationCount}`;" in source
    assert format_guest_count(0, 15) == "Гостей: 0 из 15"
    assert format_guest_count(3, None) == "Гостей: 3"


def test_frontend_src_has_no_guest_suffix_name():
    hits = [
        path.relative_to(FRONTEND_SRC).as_posix()
        for path in FRONTEND_SRC.rglob("*")
        if path.suffix in {".ts", ".tsx", ".css"} and "Плюша" in path.read_text(encoding="utf-8")
    ]
    assert hits == []


def _message(*, text: str | None, caption: str | None = None) -> MagicMock:
    message = MagicMock()
    message.text = text
    message.caption = caption
    message.answer = AsyncMock()
    return message


def _state() -> AsyncMock:
    state = AsyncMock()
    state.get_data.return_value = {}
    return state


async def test_create_description_stores_caption_and_rejects_empty():
    state = _state()
    captioned = _message(text=None, caption="  Приходите в костюмах  ")
    await create_description(captioned, state)
    state.update_data.assert_awaited_once_with(description="Приходите в костюмах")
    state.set_state.assert_awaited_once_with(AdminStates.CREATE_CAPACITY)

    state.reset_mock()
    empty = _message(text=None, caption="   ")
    await create_description(empty, state)
    state.update_data.assert_not_called()
    state.set_state.assert_not_called()
    empty.answer.assert_awaited()


async def test_edit_description_stores_caption_and_rejects_empty():
    state = _state()
    captioned = _message(text=None, caption="Новый текст")
    await edit_description(captioned, state)
    state.update_data.assert_awaited_once_with(description="Новый текст")

    state.reset_mock()
    empty = _message(text=None, caption=None)
    await edit_description(empty, state)
    state.update_data.assert_not_called()
    empty.answer.assert_awaited()
