from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

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
        # Create returns the raw model because auto_convert is False in the repo
        created_note_model = await self.note_repo.create(note, user_id=author_id)

        # Re-fetch with relationships to allow for correct Pydantic validation
        loaded_note = await self.note_repo.get_by_id(
            created_note_model.id, options=[selectinload(TicketNote.attachments)]
        )
        if not loaded_note:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create note.")

        return TicketNoteRead.model_validate(loaded_note, from_attributes=True)

    async def create_system_event(
        self,
        ticket_id: int,
        author_id: int,
        event_type: TicketEventType,
        event_details: dict[str, Any] | None = None,
    ) -> TicketNoteRead:
        """建立系統事件"""
        note = TicketNote(
            ticket_id=ticket_id,
            author_id=author_id,
            system=True,
            event_type=event_type,
            event_details=event_details,
        )
        created_note_model = await self.note_repo.create(note, user_id=author_id)

        # Re-fetch with relationships to allow for correct Pydantic validation
        loaded_note = await self.note_repo.get_by_id(
            created_note_model.id, options=[selectinload(TicketNote.attachments)]
        )
        if not loaded_note:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create system event.")

        return TicketNoteRead.model_validate(loaded_note, from_attributes=True)