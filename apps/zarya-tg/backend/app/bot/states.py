from __future__ import annotations

from enum import Enum


class AdminStates(str, Enum):
  MENU = "menu"
  CREATE_NAME = "create_name"
  CREATE_DATE = "create_date"
  CREATE_TIME = "create_time"
  CREATE_LOCATION = "create_location"
  CREATE_DESCRIPTION = "create_description"
  CREATE_IMAGE = "create_image"
  CREATE_CONFIRM = "create_confirm"
  MANAGE_LIST = "manage_list"
  MANAGE_DETAIL = "manage_detail"
  EDIT_NAME = "edit_name"
  EDIT_DATE = "edit_date"
  EDIT_TIME = "edit_time"
  EDIT_LOCATION = "edit_location"
  EDIT_DESCRIPTION = "edit_description"
  EDIT_IMAGE = "edit_image"
  EDIT_CONFIRM = "edit_confirm"
  DELETE_CONFIRM = "delete_confirm"
