from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.registration import MAX_PARTY_SIZE_MVP, MIN_PARTY_SIZE


class RegistrationCreate(BaseModel):
    party_size: int = Field(default=MIN_PARTY_SIZE, ge=MIN_PARTY_SIZE, le=MAX_PARTY_SIZE_MVP)

    @field_validator("party_size")
    @classmethod
    def party_size_mvp(cls, value: int) -> int:
        if value < MIN_PARTY_SIZE or value > MAX_PARTY_SIZE_MVP:
            raise ValueError(f"party_size must be between {MIN_PARTY_SIZE} and {MAX_PARTY_SIZE_MVP}")
        return value


class RegistrationPartyUpdate(BaseModel):
    party_size: int = Field(ge=MIN_PARTY_SIZE, le=MAX_PARTY_SIZE_MVP)

    @field_validator("party_size")
    @classmethod
    def party_size_mvp(cls, value: int) -> int:
        if value < MIN_PARTY_SIZE or value > MAX_PARTY_SIZE_MVP:
            raise ValueError(f"party_size must be between {MIN_PARTY_SIZE} and {MAX_PARTY_SIZE_MVP}")
        return value


class RegistrationResponse(BaseModel):
    message: str
    registration_count: int
    is_registered: bool
    party_size: int = 0
