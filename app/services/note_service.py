from typing import Any

from fastapi import Depends

from app.models import TicketEventType, TicketNote
from app.repositories.note_repository import TicketNoteRepository
from app.schemas.note import TicketNoteCreate, TicketNoteRead


class NoteService:
    def __init__(self, note_repo: TicketNoteRepository = Depends(TicketNoteRepository)):
        self.note_repo = note_repo

    async def create_user_note(
        self, ticket_id: int, note_data: TicketNoteCreate, author_id: int
    ) -> TicketNoteRead:
        """建立使用者留言"""
        note = TicketNote(
            ticket_id=ticket_id,
            author_id=author_id,
            note=note_data.note,
            system=False,
        )
        created_note = await self.note_repo.create(note, user_id=author_id)
        return TicketNoteRead.model_validate(created_note, from_attributes=True)

    async def create_system_event(
        self,
        ticket_id: int,
        author_id: int,
        event_type: TicketEventType,
        event_details: dict[str, Any] | None = None,
    ) -> TicketNote:
        """建立系統事件"""
        note = TicketNote(
            ticket_id=ticket_id,
            author_id=author_id,
            system=True,
            event_type=event_type,
            event_details=event_details,
        )
        # We want the raw model back for internal use, so we don't use the schema conversion
        created_note = await self.note_repo.create(note, user_id=author_id)
        return created_note