from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    telegram_id: int
    username: str | None
    first_name: str | None
