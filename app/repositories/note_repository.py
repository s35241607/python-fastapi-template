from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import TicketNote
from app.repositories.base_repository import BaseRepository
from app.schemas.note import TicketNoteRead


class TicketNoteRepository(BaseRepository[TicketNote, TicketNote, TicketNote, TicketNoteRead]):
    model = TicketNote

    def __init__(self, session: AsyncSession = Depends(get_db)):
        # Disable auto-conversion to handle it manually in the service layer,
        # allowing for eager loading of relationships before Pydantic validation.
        super().__init__(session, schema=TicketNoteRead, auto_convert=False)