from datetime import UTC, datetime
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models import Ticket, TicketNote
from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
from app.schemas.note import TicketNoteCreate
from app.schemas.ticket import TicketStatusUpdate, TicketUpdate
from app.services.ticket_service import TicketService


class TestTicketService:
    @pytest.fixture
    def mock_ticket_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_category_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_label_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_approval_service(self):
        return AsyncMock()

    @pytest.fixture
    def mock_note_service(self):
        return AsyncMock()

    @pytest.fixture
    def mock_note_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_notification_service(self):
        return AsyncMock()

    @pytest.fixture
    def service(
        self,
        mock_ticket_repo,
        mock_category_repo,
        mock_label_repo,
        mock_approval_service,
        mock_note_service,
        mock_note_repo,
        mock_notification_service,
    ) -> TicketService:
        # Manually instantiate the service and inject mocks
        service = TicketService(
            ticket_repo=mock_ticket_repo,
            category_repo=mock_category_repo,
            label_repo=mock_label_repo,
            approval_service=mock_approval_service,
            note_service=mock_note_service,
            note_repo=mock_note_repo,
            notification_service=mock_notification_service,
        )
        return service

    def _get_mock_ticket(self, ticket_id: int, user_id: int, visibility: TicketVisibility, status: TicketStatus) -> MagicMock:
        return MagicMock(
            spec=Ticket,
            id=ticket_id,
            status=status,
            visibility=visibility,
            created_by=user_id,
            title="Test Ticket",
            description="Test Description",
            priority=TicketPriority.MEDIUM,
            ticket_no="TIC-2023-001",
            created_at=datetime.now(UTC),
            updated_by=None,
            updated_at=None,
            assigned_to=None,
            custom_fields_data={},
            categories=[],
            labels=[],
            notes=[],
            approval_process=None,  # Default to None for tests that don't need it
            view_permissions=[],
        )

    def _get_mock_note(self, note_id: int, author_id: int) -> MagicMock:
        return MagicMock(
            spec=TicketNote,
            id=note_id,
            author_id=author_id,
            note="A test comment",
            system=False,
            event_type=None,
            event_details=None,
            created_at=datetime.now(UTC),
            attachments=[],
        )

    @pytest.mark.asyncio
    async def test_get_ticket_by_id_internal(self, service: TicketService, mock_ticket_repo):
        # Arrange
        ticket_id = 1
        user_id = 123
        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)
        mock_ticket_repo.get_by_id.return_value = mock_ticket

        # Act
        result = await service.get_ticket_by_id(ticket_id, user_id)

        # Assert
        assert result is not None
        mock_ticket_repo.get_by_id.assert_called_once_with(ticket_id, options=ANY)

    @pytest.mark.asyncio
    async def test_get_ticket_by_id_restricted_allowed(self, service: TicketService, mock_ticket_repo):
        # Arrange
        ticket_id = 1
        user_id = 123
        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.RESTRICTED, TicketStatus.DRAFT)
        mock_ticket_repo.get_by_id.return_value = mock_ticket

        # Act
        result = await service.get_ticket_by_id(ticket_id, user_id)

        # Assert
        assert result is not None
        mock_ticket_repo.get_by_id.assert_called_once_with(ticket_id, options=ANY)

    @pytest.mark.asyncio
    async def test_get_ticket_by_id_restricted_forbidden(self, service: TicketService, mock_ticket_repo):
        # Arrange
        ticket_id = 1
        user_id = 123
        creator_id = 456
        mock_ticket = self._get_mock_ticket(ticket_id, creator_id, TicketVisibility.RESTRICTED, TicketStatus.DRAFT)
        mock_ticket_repo.get_by_id.return_value = mock_ticket

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.get_ticket_by_id(ticket_id, user_id)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_ticket_status_valid_transition(self, service: TicketService, mock_ticket_repo, mock_approval_service):
        # Arrange
        ticket_id = 1
        user_id = 123
        status_update = TicketStatusUpdate(status=TicketStatus.WAITING_APPROVAL, reason="Submitting for review")

        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)
        mock_ticket_repo.get_by_id.return_value = mock_ticket
        mock_ticket_repo.update.return_value = mock_ticket

        # Act
        await service.update_ticket_status(ticket_id, status_update, user_id)

        # Assert
        # It's called once at the start and once at the end to reload the data
        assert mock_ticket_repo.get_by_id.call_count == 2
        mock_approval_service.start_approval_process.assert_called_once_with(mock_ticket, user_id)
        mock_ticket_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_ticket_status_invalid_transition(self, service: TicketService, mock_ticket_repo):
        # Arrange
        ticket_id = 1
        user_id = 123
        status_update = TicketStatusUpdate(status=TicketStatus.OPEN, reason="Skipping steps")

        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)
        mock_ticket_repo.get_by_id.return_value = mock_ticket

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.update_ticket_status(ticket_id, status_update, user_id)

        assert exc_info.value.status_code == 400
        assert "Cannot change status" in exc_info.value.detail
        mock_ticket_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_ticket(self, service: TicketService, mock_ticket_repo, mock_note_service):
        # Arrange
        ticket_id = 1
        user_id = 123
        ticket_update = TicketUpdate(title="New Title")
        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)

        mock_ticket_repo.get_by_id.return_value = mock_ticket
        mock_ticket_repo.update.return_value = mock_ticket

        # Act
        await service.update_ticket(ticket_id, ticket_update, user_id)

        # Assert
        assert mock_ticket_repo.get_by_id.call_count == 2
        mock_note_service.create_system_event.assert_called_once()
        mock_ticket_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tickets_for_user(self, service: TicketService, mock_ticket_repo):
        # Arrange
        user_id = 123
        mock_tickets = [self._get_mock_ticket(1, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)]
        mock_ticket_repo.get_tickets_for_user.return_value = mock_tickets

        # Act
        result = await service.get_tickets(user_id)

        # Assert
        mock_ticket_repo.get_tickets_for_user.assert_called_once_with(user_id)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_add_user_note(self, service: TicketService, mock_ticket_repo, mock_note_service):
        # Arrange
        ticket_id = 1
        user_id = 123
        note_data = TicketNoteCreate(note="A new comment")
        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)

        mock_ticket_repo.get_by_id.return_value = mock_ticket
        mock_note_service.create_user_note.return_value = MagicMock()

        # Act
        await service.add_user_note(ticket_id, note_data, user_id)

        # Assert
        mock_ticket_repo.get_by_id.assert_called_once()
        mock_note_service.create_user_note.assert_called_once_with(
            ticket_id=ticket_id, note_data=note_data, author_id=user_id
        )

    @pytest.mark.asyncio
    async def test_get_ticket_notes(self, service: TicketService, mock_ticket_repo, mock_note_repo):
        # Arrange
        ticket_id = 1
        user_id = 123
        mock_ticket = self._get_mock_ticket(ticket_id, user_id, TicketVisibility.INTERNAL, TicketStatus.DRAFT)
        mock_notes = [self._get_mock_note(i, user_id) for i in range(3)]

        mock_ticket_repo.get_by_id.return_value = mock_ticket
        mock_note_repo.get_multi.return_value = mock_notes

        # Act
        result = await service.get_ticket_notes(ticket_id, user_id)

        # Assert
        mock_ticket_repo.get_by_id.assert_called_once()
        mock_note_repo.get_multi.assert_called_once()
        assert len(result) == 3