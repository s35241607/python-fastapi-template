from typing import cast

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from typing import cast

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


class TicketService:
    def __init__(
        self,
        ticket_repo: TicketRepository = Depends(TicketRepository),
        category_repo: CategoryRepository = Depends(CategoryRepository),
        label_repo: LabelRepository = Depends(LabelRepository),
        approval_service: ApprovalService = Depends(ApprovalService),
        note_service: NoteService = Depends(NoteService),
        note_repo: TicketNoteRepository = Depends(TicketNoteRepository),
    ):
        """Service is constructed with a TicketRepository instance.

        Contract:
        - inputs: TicketRepository
        - outputs: domain models (Ticket) or primitives
        - error modes: passes through repository exceptions as appropriate
        """
        self.ticket_repo = ticket_repo
        self.category_repo = category_repo
        self.label_repo = label_repo
        self.approval_service = approval_service
        self.note_service = note_service
        self.note_repo = note_repo

    async def create_ticket(self, ticket_data: TicketCreate, created_by: int) -> TicketRead:
        """建立新工單，包含分類和標籤關聯"""
        # 1. 取得 ticket no
        new_ticket_no: str = await self.ticket_repo.generate_ticket_no()

        # 2. 取得 category 和 label 的完整物件列表
        categorys: list[Category] = await self.category_repo.get_by_ids(ticket_data.category_ids)
        labels: list[Label] = await self.label_repo.get_by_ids(ticket_data.label_ids)

        ticket = Ticket(
            **ticket_data.model_dump(exclude={"category_ids", "label_ids"}),
            ticket_no=new_ticket_no,
            status=TicketStatus.DRAFT,
            categories=categorys,
            labels=labels,
        )

        created_ticket = await self.ticket_repo.create(ticket, created_by, preload=[Ticket.categories, Ticket.labels])
        return TicketRead.model_validate(created_ticket, from_attributes=True)

    async def get_tickets(self, current_user_id: int) -> list[TicketRead]:
        """取得使用者可見的工單列表"""
        tickets = await self.ticket_repo.get_tickets_for_user(current_user_id)
        return cast(list[TicketRead], tickets)

    async def get_ticket_by_id(self, ticket_id: int, current_user_id: int) -> TicketRead:
        """取得單一工單，包含權限檢查"""
        # 1. 取得工單基本資料，並預先載入關聯
        options = [
            selectinload(Ticket.view_permissions),
            selectinload(Ticket.approval_process).selectinload(ApprovalProcess.steps),
            selectinload(Ticket.categories),
            selectinload(Ticket.labels),
        ]
        ticket = await self.ticket_repo.get_by_id(ticket_id, options=options)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 2. 權限檢查
        if ticket.visibility == TicketVisibility.INTERNAL:
            # 內部工單，所有登入者可見
            return TicketRead.model_validate(ticket, from_attributes=True)

        if ticket.visibility == TicketVisibility.RESTRICTED:
            # 檢查是否為開單者
            if ticket.created_by == current_user_id:
                return TicketRead.model_validate(ticket, from_attributes=True)

            # TODO: 檢查是否為簽核人
            # TODO: 檢查是否在 ticket_view_permissions 中

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this ticket")

        # Fallback, should not happen
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    async def update_ticket(self, ticket_id: int, ticket_update: TicketUpdate, current_user_id: int) -> TicketRead:
        """更新工單，包含權限檢查與變更紀錄"""
        # 1. 取得工單
        original_ticket = await self.ticket_repo.get_by_id(ticket_id, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)])
        if not original_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 2. 權限檢查 (暫定只有開單者能修改)
        if original_ticket.created_by != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the ticket creator can update the ticket")

        # 3. 準備更新資料並記錄變更
        update_data = ticket_update.model_dump(exclude_unset=True, exclude={"category_ids", "label_ids"})
        for field, value in update_data.items():
            original_value = getattr(original_ticket, field)
            if original_value != value:
                await self.note_service.create_system_event(
                    ticket_id=ticket_id,
                    author_id=current_user_id,
                    event_type=TicketEventType[f"{field.upper()}_CHANGE"],
                    event_details={"from": str(original_value), "to": str(value)},
                )

        # 4. 處理關聯更新 (Categories & Labels)
        if ticket_update.category_ids is not None:
            # This is a simplified version; a real implementation would log additions/removals.
            original_ticket.categories = await self.category_repo.get_by_ids(ticket_update.category_ids)
        if ticket_update.label_ids is not None:
            original_ticket.labels = await self.label_repo.get_by_ids(ticket_update.label_ids)

        # 5. 更新工單主體
        for field, value in update_data.items():
            setattr(original_ticket, field, value)

        # 6. 儲存變更
        updated_ticket = await self.ticket_repo.update(original_ticket.id, original_ticket, user_id=current_user_id)

        # 7. 重新載入關聯以確保回傳資料的完整性
        reloaded_ticket = await self.ticket_repo.get_by_id(
            updated_ticket.id, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        return TicketRead.model_validate(reloaded_ticket, from_attributes=True)

    async def update_ticket_status(
        self, ticket_id: int, status_update: TicketStatusUpdate, current_user_id: int
    ) -> TicketRead:
        """更新工單狀態，包含生命週期檢查"""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        current_status = ticket.status
        new_status = status_update.status

        # 根據 SPEC 定義的狀態機
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

        # TODO: 根據角色檢查權限 (e.g., 只有建立者可以從 DRAFT -> WAITING_APPROVAL)
        # For now, we allow any logged-in user to change status if the transition is valid.

        # 觸發附帶動作 (Side Effects)
        if new_status == TicketStatus.WAITING_APPROVAL:
            await self.approval_service.start_approval_process(ticket, current_user_id)

        # 更新狀態
        ticket.status = new_status
        updated_ticket = await self.ticket_repo.update(ticket_id, ticket, current_user_id)

        # 記錄系統事件
        await self.note_service.create_system_event(
            ticket_id=ticket_id,
            author_id=current_user_id,
            event_type=TicketEventType.STATUS_CHANGE,
            event_details={"from": current_status.value, "to": new_status.value, "reason": status_update.reason},
        )

        return TicketRead.model_validate(updated_ticket, from_attributes=True)

    async def get_ticket_notes(self, ticket_id: int, current_user_id: int) -> list[TicketNoteRead]:
        """取得工單的完整時間軸，包含權限檢查"""
        # 權限檢查: 借用 get_ticket_by_id 的邏輯，如果使用者能看到 ticket，就能看到 notes
        await self.get_ticket_by_id(ticket_id, current_user_id)

        notes = await self.note_repo.get_multi(
            filters={"ticket_id": ticket_id},
            options=[selectinload(TicketNote.attachments)],
            # TODO: Add sorting
        )
        return [TicketNoteRead.model_validate(note, from_attributes=True) for note in notes]

    async def add_user_note(
        self, ticket_id: int, note_data: TicketNoteCreate, current_user_id: int
    ) -> TicketNoteRead:
        """新增使用者留言，包含權限檢查"""
        # 權限檢查: 借用 get_ticket_by_id 的邏輯
        await self.get_ticket_by_id(ticket_id, current_user_id)

        created_note = await self.note_service.create_user_note(
            ticket_id=ticket_id, note_data=note_data, author_id=current_user_id
        )

        # TODO: 觸發 on_new_comment 通知

        return created_note
