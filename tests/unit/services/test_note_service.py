from datetime import UTC, datetime
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import selectinload

from app.models import TicketEventType, TicketNote
from app.repositories.note_repository import TicketNoteRepository
from app.schemas.note import TicketNoteCreate, TicketNoteRead
from app.services.note_service import NoteService


class TestNoteService:
    @pytest.fixture
    def mock_note_repo(self) -> AsyncMock:
        return AsyncMock(spec=TicketNoteRepository)

    @pytest.fixture
    def service(self, mock_note_repo: AsyncMock) -> NoteService:
        return NoteService(note_repo=mock_note_repo)

    def _get_mock_note(
        self, note_id: int, author_id: int, note_text: str | None, is_system: bool = False
    ) -> MagicMock:
        """Helper to create a mock TicketNote object."""
        return MagicMock(
            spec=TicketNote,
            id=note_id,
            author_id=author_id,
            note=note_text,
            system=is_system,
            event_type=TicketEventType.STATUS_CHANGE if is_system else None,
            event_details={"from": "open", "to": "closed"} if is_system else None,
            created_at=datetime.now(UTC),
            attachments=[],
        )

    @pytest.mark.asyncio
    async def test_create_user_note(self, service: NoteService, mock_note_repo: AsyncMock):
        # Arrange
        ticket_id = 1
        author_id = 10
        note_data = TicketNoteCreate(note="This is a user comment.")

        # Ensure the mock note has the correct text for the assertion
        mock_created_note = self._get_mock_note(
            note_id=99, author_id=author_id, note_text=note_data.note, is_system=False
        )
        mock_note_repo.create.return_value = mock_created_note
        mock_note_repo.get_by_id.return_value = mock_created_note

        # Act
        result = await service.create_user_note(ticket_id, note_data, author_id)

        # Assert
        mock_note_repo.create.assert_called_once()
        mock_note_repo.get_by_id.assert_called_once_with(
            mock_created_note.id, options=[ANY]
        )
        assert isinstance(result, TicketNoteRead)
        assert result.id == mock_created_note.id
        assert result.note == note_data.note

    @pytest.mark.asyncio
    async def test_create_system_event(self, service: NoteService, mock_note_repo: AsyncMock):
        # Arrange
        ticket_id = 1
        author_id = 10
        event_type = TicketEventType.STATUS_CHANGE
        event_details = {"from": "open", "to": "closed"}

        mock_created_note = self._get_mock_note(
            note_id=100, author_id=author_id, note_text=None, is_system=True
        )
        mock_note_repo.create.return_value = mock_created_note
        mock_note_repo.get_by_id.return_value = mock_created_note

        # Act
        result = await service.create_system_event(
            ticket_id, author_id, event_type, event_details
        )

        # Assert
        mock_note_repo.create.assert_called_once()
        mock_note_repo.get_by_id.assert_called_once_with(
            mock_created_note.id, options=[ANY]
        )
        assert isinstance(result, TicketNoteRead)
        assert result.id == mock_created_note.id
        assert result.system is True
        assert result.event_type == event_type