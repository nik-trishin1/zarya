from datetime import date as date_type, time as time_type

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    name: str
    description: str
    date: date_type
    time: time_type
    location: str
    cover_image_url: str | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    date: date_type | None = None
    time: time_type | None = None
    location: str | None = None
    cover_image_url: str | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    name: str
    description: str
    date: date_type
    time: time_type
    location: str
    cover_image_url: str | None
    registration_count: int = 0
    is_registered: bool = False


class EventDetailResponse(EventResponse):
    pass


class MessageResponse(BaseModel):
    message: str
