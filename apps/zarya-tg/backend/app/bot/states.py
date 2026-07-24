from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    MENU = State()
    CREATE_NAME = State()
    CREATE_DATE = State()
    CREATE_TIME = State()
    CREATE_LOCATION = State()
    CREATE_DESCRIPTION = State()
    CREATE_CAPACITY = State()
    CREATE_AUDIENCE = State()
    CREATE_IMAGE = State()
    CREATE_CONFIRM = State()
    MANAGE_LIST = State()
    MANAGE_DETAIL = State()
    EDIT_NAME = State()
    EDIT_DATE = State()
    EDIT_TIME = State()
    EDIT_LOCATION = State()
    EDIT_DESCRIPTION = State()
    EDIT_IMAGE = State()
    EDIT_CONFIRM = State()
    DELETE_CONFIRM = State()
    BROADCAST_MESSAGE = State()
    BROADCAST_CONFIRM = State()
    ALL_BROADCAST_MESSAGE = State()
    ALL_BROADCAST_CONFIRM = State()
    GROUP_BROADCAST_PICK = State()
    GROUP_BROADCAST_MESSAGE = State()
    GROUP_BROADCAST_CONFIRM = State()
