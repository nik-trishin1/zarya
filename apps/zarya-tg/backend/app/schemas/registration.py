from __future__ import annotations

from pydantic import BaseModel


class RegistrationResponse(BaseModel):
    message: str
    registration_count: int
    is_registered: bool
