from datetime import UTC, datetime
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models import (
    ApprovalProcess,
    ApprovalProcessStep,
    ApprovalTemplate,
    ApprovalTemplateStep,
    Ticket,
    TicketStatus,
)
from app.models.enums import ApprovalProcessStatus, ApprovalProcessStepStatus
from app.schemas.approval import ApprovalAction
from app.services.approval_service import ApprovalService


class TestApprovalService:
    @pytest.fixture
    def mock_approval_process_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_approval_process_step_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_approval_template_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_ticket_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_note_service(self):
        return AsyncMock()

    @pytest.fixture
    def service(
        self,
        mock_approval_process_repo,
        mock_approval_process_step_repo,
        mock_approval_template_repo,
        mock_ticket_repo,
        mock_note_service,
    ) -> ApprovalService:
        return ApprovalService(
            approval_process_repo=mock_approval_process_repo,
            approval_process_step_repo=mock_approval_process_step_repo,
            approval_template_repo=mock_approval_template_repo,
            ticket_repo=mock_ticket_repo,
            note_service=mock_note_service,
        )

    def _get_mock_template(self, template_id: int, with_steps: bool = True) -> MagicMock:
        template = MagicMock(spec=ApprovalTemplate)
        template.id = template_id
        template.name = "Test Template"
        if with_steps:
            step1 = MagicMock(spec=ApprovalTemplateStep, step_order=1, user_id=101)
            step2 = MagicMock(spec=ApprovalTemplateStep, step_order=2, user_id=102)
            template.steps = [step1, step2]
        else:
            template.steps = []
        return template

    def _get_mock_ticket(self, ticket_id: int, template_id: int | None) -> MagicMock:
        ticket = MagicMock(spec=Ticket)
        ticket.id = ticket_id
        ticket.approval_template_id = template_id
        return ticket

    def _get_mock_process_and_steps(self, process_id: int, current_step_order: int, total_steps: int) -> MagicMock:
        process = MagicMock(spec=ApprovalProcess)
        process.id = process_id
        process.current_step = current_step_order
        process.status = ApprovalProcessStatus.PENDING

        steps = []
        for i in range(1, total_steps + 1):
            step = MagicMock(spec=ApprovalProcessStep)
            step.id = i * 100
            step.step_order = i
            step.approver_id = i * 10
            step.status = ApprovalProcessStepStatus.PENDING
            step.approval_process = process
            steps.append(step)

        process.steps = steps
        return process, steps

    @pytest.mark.asyncio
    async def test_start_approval_process_success(self, service: ApprovalService, mock_approval_template_repo, mock_approval_process_repo):
        # Arrange
        user_id = 1
        ticket = self._get_mock_ticket(ticket_id=10, template_id=20)
        template = self._get_mock_template(template_id=20)
        mock_approval_template_repo.get_by_id.return_value = template

        # We need to mock the return value of the create call to verify it
        created_process = MagicMock(spec=ApprovalProcess)
        mock_approval_process_repo.create.return_value = created_process

        # Act
        result = await service.start_approval_process(ticket, user_id)

        # Assert
        mock_approval_template_repo.get_by_id.assert_called_once_with(20, options=ANY)
        mock_approval_process_repo.create.assert_called_once()

        # Check the created process object before it's saved
        created_process_args = mock_approval_process_repo.create.call_args[0][0]
        assert isinstance(created_process_args, ApprovalProcess)
        assert created_process_args.ticket_id == 10
        assert created_process_args.approval_template_id == 20
        assert created_process_args.status == ApprovalProcessStatus.PENDING
        assert len(created_process_args.steps) == 2
        assert created_process_args.steps[0].approver_id == 101
        assert created_process_args.steps[1].approver_id == 102

        assert result == created_process
        service.note_service.create_system_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_approval_process_no_template_id(self, service: ApprovalService):
        # Arrange
        user_id = 1
        ticket = self._get_mock_ticket(ticket_id=10, template_id=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.start_approval_process(ticket, user_id)

        assert exc_info.value.status_code == 400
        assert "requires an approval template" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_approval_process_template_not_found(self, service: ApprovalService, mock_approval_template_repo):
        # Arrange
        user_id = 1
        ticket = self._get_mock_ticket(ticket_id=10, template_id=99)
        mock_approval_template_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.start_approval_process(ticket, user_id)

        assert exc_info.value.status_code == 404
        assert "template not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_approve_step_advances_process(self, service: ApprovalService, mock_approval_process_step_repo, mock_ticket_repo):
        # Arrange
        process, steps = self._get_mock_process_and_steps(process_id=1, current_step_order=1, total_steps=2)
        current_step = steps[0]
        action = ApprovalAction(comment="LGTM")
        current_user_id = current_step.approver_id

        mock_approval_process_step_repo.get_by_id.return_value = current_step
        mock_approval_process_step_repo.update.return_value = current_step

        # Act
        await service.approve_step(current_step.id, action, current_user_id)

        # Assert
        assert process.current_step == 2
        assert process.status == ApprovalProcessStatus.PENDING  # Not yet approved
        mock_ticket_repo.update.assert_not_called() # Ticket status should not change yet
        service.note_service.create_system_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_final_step_completes_process(self, service: ApprovalService, mock_approval_process_step_repo, mock_ticket_repo):
        # Arrange
        process, steps = self._get_mock_process_and_steps(process_id=1, current_step_order=2, total_steps=2)
        final_step = steps[1]
        action = ApprovalAction(comment="All approved")
        current_user_id = final_step.approver_id

        mock_approval_process_step_repo.get_by_id.return_value = final_step
        mock_approval_process_step_repo.update.return_value = final_step

        # Act
        await service.approve_step(final_step.id, action, current_user_id)

        # Assert
        assert process.status == ApprovalProcessStatus.APPROVED
        mock_ticket_repo.update.assert_called_once_with(process.ticket_id, {"status": TicketStatus.OPEN}, user_id=current_user_id)
        service.note_service.create_system_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_step_completes_process(self, service: ApprovalService, mock_approval_process_step_repo, mock_ticket_repo):
        # Arrange
        process, steps = self._get_mock_process_and_steps(process_id=1, current_step_order=1, total_steps=2)
        current_step = steps[0]
        action = ApprovalAction(comment="Rejected")
        current_user_id = current_step.approver_id

        mock_approval_process_step_repo.get_by_id.return_value = current_step

        # Act
        await service.reject_step(current_step.id, action, current_user_id)

        # Assert
        assert process.status == ApprovalProcessStatus.REJECTED
        mock_ticket_repo.update.assert_called_once_with(process.ticket_id, {"status": TicketStatus.REJECTED}, user_id=current_user_id)
        service.note_service.create_system_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_action_on_step_permission_denied(self, service: ApprovalService, mock_approval_process_step_repo):
        # Arrange
        process, steps = self._get_mock_process_and_steps(process_id=1, current_step_order=1, total_steps=2)
        current_step = steps[0]
        action = ApprovalAction(comment="Trying to approve")
        wrong_user_id = 999

        mock_approval_process_step_repo.get_by_id.return_value = current_step

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.approve_step(current_step.id, action, wrong_user_id)

        assert exc_info.value.status_code == 403
        assert "not the designated approver" in exc_info.value.detail