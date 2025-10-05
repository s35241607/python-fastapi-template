from typing import Any, cast

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from app.models import (
    ApprovalProcess,
    Category,
    Label,
    Ticket,
    TicketEventType,
    TicketNote,
    TicketStatus,
    TicketVisibility,
)
from app.repositories.category_repository import CategoryRepository
from app.repositories.label_repository import LabelRepository
from app.repositories.note_repository import TicketNoteRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.note import TicketNoteCreate, TicketNoteRead
from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.approval_service import ApprovalService
from app.services.note_service import NoteService
from app.services.notification_service import NotificationEvent, NotificationService


class TicketService:
    def __init__(
        self,
        ticket_repo: TicketRepository = Depends(TicketRepository),
        category_repo: CategoryRepository = Depends(CategoryRepository),
        label_repo: LabelRepository = Depends(LabelRepository),
        approval_service: ApprovalService = Depends(ApprovalService),
        note_service: NoteService = Depends(NoteService),
        note_repo: TicketNoteRepository = Depends(TicketNoteRepository),
        notification_service: NotificationService = Depends(NotificationService),
    ):
        self.ticket_repo = ticket_repo
        self.category_repo = category_repo
        self.label_repo = label_repo
        self.approval_service = approval_service
        self.note_service = note_service
        self.note_repo = note_repo
        self.notification_service = notification_service

        self._full_load_options = [
            selectinload(Ticket.categories),
            selectinload(Ticket.labels),
            selectinload(Ticket.notes).selectinload(TicketNote.attachments),
            selectinload(Ticket.approval_process).selectinload(ApprovalProcess.steps),
            selectinload(Ticket.view_permissions),
        ]

    async def _log_ticket_updates(self, ticket_id: int, user_id: int, original_ticket: Ticket, update_data: dict[str, Any]):
        """Helper function to log changes to a ticket as system notes."""
        field_to_event_map = {
            "title": TicketEventType.TITLE_CHANGE,
            "description": TicketEventType.DESCRIPTION_CHANGE,
            "status": TicketEventType.STATUS_CHANGE,
            "priority": TicketEventType.PRIORITY_CHANGE,
            "assigned_to": TicketEventType.ASSIGNED_TO_CHANGE,
            "due_date": TicketEventType.DUE_DATE_CHANGE,
        }

        for field, value in update_data.items():
            original_value = getattr(original_ticket, field)
            if original_value != value:
                event_type = field_to_event_map.get(field)
                if event_type:
                    await self.note_service.create_system_event(
                        ticket_id=ticket_id,
                        author_id=user_id,
                        event_type=event_type,
                        event_details={"from": str(original_value), "to": str(value)},
                    )

    async def create_ticket(self, ticket_data: TicketCreate, created_by: int) -> TicketRead:
        """建立新工單，包含分類和標籤關聯"""
        # 1. 取得 ticket no
        new_ticket_no: str = await self.ticket_repo.generate_ticket_no()

        # 2. 取得 category 和 label 的完整物件列表
        categories: list[Category] = await self.category_repo.get_by_ids(ticket_data.category_ids)
        labels: list[Label] = await self.label_repo.get_by_ids(ticket_data.label_ids)

        # Manually construct the Ticket object to ensure full control
        db_obj = Ticket(
            **ticket_data.model_dump(exclude={"category_ids", "label_ids"}),
            ticket_no=new_ticket_no,
            status=TicketStatus.DRAFT,
            created_by=created_by,
        )
        db_obj.categories = categories
        db_obj.labels = labels

        created_ticket_model = await self.ticket_repo.create(db_obj, user_id=created_by)

        # Re-fetch the ticket with all necessary relationships eagerly loaded
        loaded_ticket = await self.ticket_repo.get_by_id(
            created_ticket_model.id, options=self._full_load_options
        )
        if not loaded_ticket:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create ticket.")

        # Trigger notification
        await self.notification_service.trigger_event(NotificationEvent.ON_CREATE, loaded_ticket)

        return cast(TicketRead, loaded_ticket)

    async def get_tickets(self, current_user_id: int) -> list[TicketRead]:
        """取得使用者可見的工單列表"""
        tickets = await self.ticket_repo.get_tickets_for_user(current_user_id)
        return cast(list[TicketRead], tickets)

    async def get_ticket_by_id(self, ticket_id: int, current_user_id: int) -> TicketRead:
        """取得單一工單，包含權限檢查"""
        ticket = await self.ticket_repo.get_by_id(ticket_id, options=self._full_load_options)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        ticket_read = cast(TicketRead, ticket)

        if ticket_read.visibility == TicketVisibility.INTERNAL:
            return ticket_read

        if ticket_read.visibility == TicketVisibility.RESTRICTED:
            allowed_user_ids = {ticket_read.created_by, ticket_read.assigned_to}

            if ticket_read.approval_process:
                for step in ticket_read.approval_process.steps:
                    if step.approver_id:
                        allowed_user_ids.add(step.approver_id)
                    if step.proxy_id:
                        allowed_user_ids.add(step.proxy_id)

            for permission in ticket_read.view_permissions:
                if permission.user_id:
                    allowed_user_ids.add(permission.user_id)

            if current_user_id in allowed_user_ids:
                return ticket_read

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this ticket")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    async def update_ticket(self, ticket_id: int, ticket_update: TicketUpdate, current_user_id: int) -> TicketRead:
        """更新工單，包含權限檢查與變更紀錄"""
        original_ticket = await self.ticket_repo.get_by_id(ticket_id, options=self._full_load_options)
        if not original_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        if original_ticket.created_by != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the ticket creator can update the ticket")

        update_data = ticket_update.model_dump(exclude_unset=True, exclude={"category_ids", "label_ids"})

        # Create system events for changes
        self._log_ticket_updates(ticket_id, current_user_id, original_ticket, update_data)

        # Pass a clean dict to the repository to avoid session conflicts
        updated_ticket_model = await self.ticket_repo.update(ticket_id, update_data, user_id=current_user_id)

        if ticket_update.category_ids is not None:
            updated_ticket_model.categories = await self.category_repo.get_by_ids(ticket_update.category_ids)
        if ticket_update.label_ids is not None:
            updated_ticket_model.labels = await self.label_repo.get_by_ids(ticket_update.label_ids)

        await self.ticket_repo.db.commit()

        reloaded_ticket = await self.ticket_repo.get_by_id(ticket_id, options=self._full_load_options)
        if not reloaded_ticket:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reload ticket after update.")

        # Trigger notifications for changes that occurred.
        update_fields = ticket_update.model_dump(exclude_unset=True)
        if "assigned_to" in update_fields and original_ticket.assigned_to != update_fields["assigned_to"]:
            await self.notification_service.trigger_event(NotificationEvent.ON_STATUS_CHANGE, reloaded_ticket)

        return cast(TicketRead, reloaded_ticket)


    async def update_ticket_status(
        self, ticket_id: int, status_update: TicketStatusUpdate, current_user_id: int
    ) -> TicketRead:
        """更新工單狀態，包含生命週期檢查"""
        ticket = await self.ticket_repo.get_by_id(
            ticket_id, options=self._full_load_options
        )
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        current_status = ticket.status
        new_status = status_update.status

        allowed_transitions = {
            TicketStatus.DRAFT: [TicketStatus.WAITING_APPROVAL, TicketStatus.CANCELLED],
            TicketStatus.WAITING_APPROVAL: [TicketStatus.REJECTED, TicketStatus.OPEN],
            TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED],
            TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED],
            TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
        }
        if new_status not in allowed_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from {current_status.value} to {new_status.value}",
            )

        is_creator = ticket.created_by == current_user_id
        is_assignee = ticket.assigned_to == current_user_id
        is_any_approver = False
        if ticket.approval_process:
            is_any_approver = any(
                step.approver_id == current_user_id or step.proxy_id == current_user_id
                for step in ticket.approval_process.steps
            )

        permission_rules = {
            (TicketStatus.DRAFT, TicketStatus.WAITING_APPROVAL): is_creator,
            (TicketStatus.DRAFT, TicketStatus.CANCELLED): is_creator,
            (TicketStatus.WAITING_APPROVAL, TicketStatus.REJECTED): is_any_approver,
            (TicketStatus.WAITING_APPROVAL, TicketStatus.OPEN): is_any_approver,
            (TicketStatus.OPEN, TicketStatus.IN_PROGRESS): is_assignee,
            (TicketStatus.OPEN, TicketStatus.CANCELLED): is_creator,
            (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED): is_assignee,
            (TicketStatus.RESOLVED, TicketStatus.CLOSED): is_creator,
            (TicketStatus.RESOLVED, TicketStatus.IN_PROGRESS): is_creator,
        }

        transition = (current_status, new_status)
        if not permission_rules.get(transition, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this status change.",
            )

        if new_status == TicketStatus.WAITING_APPROVAL:
            await self.approval_service.start_approval_process(ticket, current_user_id)

        await self.ticket_repo.update(ticket_id, {"status": new_status}, user_id=current_user_id)

        await self.note_service.create_system_event(
            ticket_id=ticket_id,
            author_id=current_user_id,
            event_type=TicketEventType.STATUS_CHANGE,
            event_details={"from": current_status.value, "to": new_status.value, "reason": status_update.reason},
        )

        reloaded_ticket = await self.ticket_repo.get_by_id(ticket_id, options=self._full_load_options)
        if not reloaded_ticket:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reload ticket after status update.")

        # Trigger notification for status change
        if new_status in [TicketStatus.CLOSED, TicketStatus.CANCELLED]:
            await self.notification_service.trigger_event(NotificationEvent.ON_CLOSE, reloaded_ticket)
        else:
            await self.notification_service.trigger_event(NotificationEvent.ON_STATUS_CHANGE, reloaded_ticket)

        return cast(TicketRead, reloaded_ticket)

    async def get_ticket_notes(self, ticket_id: int, current_user_id: int) -> list[TicketNoteRead]:
        """取得工單的完整時間軸，包含權限檢查"""
        await self.get_ticket_by_id(ticket_id, current_user_id)
        notes = await self.note_repo.get_multi(
            filters={"ticket_id": ticket_id},
            options=[selectinload(TicketNote.attachments)],
        )
        return cast(list[TicketNoteRead], notes)

    async def add_user_note(
        self, ticket_id: int, note_data: TicketNoteCreate, current_user_id: int
    ) -> TicketNoteRead:
        """新增使用者留言，包含權限檢查"""
        # Perform permission check and get the ticket data in one go.
        # This returns a TicketRead schema object.
        ticket_read = await self.get_ticket_by_id(ticket_id, current_user_id)

        created_note = await self.note_service.create_user_note(
            ticket_id=ticket_id, note_data=note_data, author_id=current_user_id
        )

        # Trigger notification using the already-fetched ticket data
        await self.notification_service.trigger_event(NotificationEvent.ON_NEW_COMMENT, ticket_read)

        return created_note