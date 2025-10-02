from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import TicketEventType


class TicketNoteAttachmentRead(BaseModel):
    id: int
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketNoteRead(BaseModel):
    id: int
    author_id: int
    note: str | None
    system: bool
    event_type: TicketEventType | None
    event_details: dict[str, Any] | None
    created_at: datetime
    attachments: list[TicketNoteAttachmentRead] = []

    class Config:
        from_attributes = True


class TicketNoteCreate(BaseModel):
    note: str = Field(..., min_length=1)
    # Attachment handling will be done separately