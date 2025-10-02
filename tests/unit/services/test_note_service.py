from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import TicketEventType, TicketNote
from app.schemas.note import TicketNoteCreate
from app.services.note_service import NoteService


class TestNoteService:
    @pytest.fixture
    def mock_note_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_note_repo) -> NoteService:
        return NoteService(note_repo=mock_note_repo)

    @pytest.mark.asyncio
    async def test_create_user_note(self, service: NoteService, mock_note_repo):
        # Arrange
        ticket_id = 1
        author_id = 10
        note_data = TicketNoteCreate(note="This is a user comment.")

        # Mock the repository's create method to return a mock object
        mock_created_note = MagicMock(
            spec=TicketNote,
            id=99,
            author_id=author_id,
            note=note_data.note,
            system=False,
            event_type=None,
            event_details=None,
            created_at=datetime.now(UTC),
            attachments=[],
        )
        mock_note_repo.create.return_value = mock_created_note

        # Act
        await service.create_user_note(ticket_id, note_data, author_id)

        # Assert
        mock_note_repo.create.assert_called_once()
        created_note_args = mock_note_repo.create.call_args[0][0]

        assert isinstance(created_note_args, TicketNote)
        assert created_note_args.ticket_id == ticket_id
        assert created_note_args.author_id == author_id
        assert created_note_args.note == note_data.note
        assert created_note_args.system is False
        assert created_note_args.event_type is None
        assert created_note_args.event_details is None

    @pytest.mark.asyncio
    async def test_create_system_event(self, service: NoteService, mock_note_repo):
        # Arrange
        ticket_id = 1
        author_id = 10
        event_type = TicketEventType.STATUS_CHANGE
        event_details = {"from": "open", "to": "closed"}

        # Mock the repository's create method
        mock_created_note = MagicMock(spec=TicketNote)
        mock_note_repo.create.return_value = mock_created_note

        # Act
        await service.create_system_event(ticket_id, author_id, event_type, event_details)

        # Assert
        mock_note_repo.create.assert_called_once()
        created_note_args = mock_note_repo.create.call_args[0][0]

        assert isinstance(created_note_args, TicketNote)
        assert created_note_args.ticket_id == ticket_id
        assert created_note_args.author_id == author_id
        assert created_note_args.system is True
        assert created_note_args.event_type == event_type
        assert created_note_args.event_details == event_details
        assert created_note_args.note is None