from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from datetime import datetime

from app.models import (
    ApprovalProcess,
    ApprovalProcessStep,
    ApprovalTemplate,
    Ticket,
    TicketEventType,
    TicketStatus,
)
from app.models.approval_process import ApprovalProcess
from app.models.enums import ApprovalProcessStatus, ApprovalProcessStepStatus
from app.repositories.approval_repository import (
    ApprovalProcessRepository,
    ApprovalProcessStepRepository,
    ApprovalTemplateRepository,
)
from app.repositories.ticket_repository import TicketRepository
from app.schemas.approval import ApprovalAction
from app.services.note_service import NoteService


class ApprovalService:
    def __init__(
        self,
        approval_process_repo: ApprovalProcessRepository = Depends(ApprovalProcessRepository),
        approval_process_step_repo: ApprovalProcessStepRepository = Depends(ApprovalProcessStepRepository),
        approval_template_repo: ApprovalTemplateRepository = Depends(ApprovalTemplateRepository),
        ticket_repo: TicketRepository = Depends(TicketRepository),
        note_service: NoteService = Depends(NoteService),
    ):
        self.approval_process_repo = approval_process_repo
        self.approval_process_step_repo = approval_process_step_repo
        self.approval_template_repo = approval_template_repo
        self.ticket_repo = ticket_repo
        self.note_service = note_service

    async def start_approval_process(self, ticket: Ticket, created_by: int) -> ApprovalProcess:
        """根據 Ticket 的 approval_template_id 啟動簽核流程"""
        if not ticket.approval_template_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket requires an approval template to start the process.",
            )

        # 1. 取得簽核範本，並預先載入其步驟
        template = await self.approval_template_repo.get_by_id(
            ticket.approval_template_id, options=[selectinload(ApprovalTemplate.steps)]
        )
        if not template or not template.steps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval template not found or has no steps.",
            )

        # 2. 建立簽核流程主體 (ApprovalProcess)
        approval_process = ApprovalProcess(
            ticket_id=ticket.id,
            approval_template_id=template.id,
            status=ApprovalProcessStatus.PENDING,
            current_step=1,
        )

        # 3. 根據範本步驟建立簽核流程的每一個步驟 (ApprovalProcessStep)
        for template_step in sorted(template.steps, key=lambda s: s.step_order):
            # TODO: 實作 role_id -> user_id 的解析邏輯
            if template_step.role_id and not template_step.user_id:
                raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Role-based approver resolution is not yet implemented.")

            process_step = ApprovalProcessStep(
                approval_process=approval_process,  # Back-reference
                step_order=template_step.step_order,
                approver_id=template_step.user_id, # Assumes user_id is present for now
                status=ApprovalProcessStepStatus.PENDING,
            )
            # The step is automatically added to the approval_process.steps collection
            # via the back-populating relationship.

        # 4. 儲存
        created_process = await self.approval_process_repo.create(approval_process, user_id=created_by)

        # 5. 記錄系統事件
        await self.note_service.create_system_event(
            ticket_id=ticket.id,
            author_id=created_by,
            event_type=TicketEventType.APPROVAL_SUBMITTED,
            event_details={"template_name": template.name},
        )

        return created_process

    async def approve_step(self, step_id: int, action: ApprovalAction, current_user_id: int) -> ApprovalProcess:
        return await self._action_on_step(step_id, ApprovalProcessStepStatus.APPROVED, action, current_user_id)

    async def reject_step(self, step_id: int, action: ApprovalAction, current_user_id: int) -> ApprovalProcess:
        return await self._action_on_step(step_id, ApprovalProcessStepStatus.REJECTED, action, current_user_id)

    async def _action_on_step(
        self, step_id: int, new_status: ApprovalProcessStepStatus, action: ApprovalAction, current_user_id: int
    ) -> ApprovalProcess:
        """對簽核步驟執行操作 (核准/駁回) 的核心邏輯"""
        # 1. 取得步驟與其關聯的流程
        options = [selectinload(ApprovalProcessStep.approval_process).selectinload(ApprovalProcess.steps)]
        step = await self.approval_process_step_repo.get_by_id(step_id, options=options)
        if not step or not step.approval_process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval step not found.")

        process = step.approval_process

        # 2. 權限與狀態檢查
        if step.approver_id != current_user_id:
            # TODO: 增加代理人檢查
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the designated approver for this step.")
        if step.status != ApprovalProcessStepStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"This step has already been actioned with status: {step.status.value}")
        if process.current_step != step.step_order:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This is not the current approval step.")

        # 3. 更新步驟狀態
        step.status = new_status
        step.comment = action.comment
        step.action_at = datetime.utcnow()
        await self.approval_process_step_repo.update(step.id, step, user_id=current_user_id)

        # 4. 處理流程推進
        if new_status == ApprovalProcessStepStatus.APPROVED:
            total_steps = len(process.steps)
            if process.current_step == total_steps:
                # 最後一關核准 -> 整個流程結束
                process.status = ApprovalProcessStatus.APPROVED
                await self.ticket_repo.update(process.ticket_id, {"status": TicketStatus.OPEN}, user_id=current_user_id)
            else:
                # 非最後一關 -> 推進到下一步
                process.current_step += 1

        elif new_status == ApprovalProcessStepStatus.REJECTED:
            # 任一關駁回 -> 整個流程結束
            process.status = ApprovalProcessStatus.REJECTED
            await self.ticket_repo.update(process.ticket_id, {"status": TicketStatus.REJECTED}, user_id=current_user_id)

        # 5. 儲存 process 的變更
        await self.approval_process_repo.update(process.id, process, user_id=current_user_id)

        # 6. 記錄系統事件
        event_type = (
            TicketEventType.APPROVAL_APPROVED
            if new_status == ApprovalProcessStepStatus.APPROVED
            else TicketEventType.APPROVAL_REJECTED
        )
        await self.note_service.create_system_event(
            ticket_id=process.ticket_id,
            author_id=current_user_id,
            event_type=event_type,
            event_details={"step": step.step_order, "approver_id": current_user_id, "comment": action.comment},
        )

        # 7. 回傳更新後的整個流程
        reloaded_process = await self.approval_process_repo.get_by_id(process.id, options=[selectinload(ApprovalProcess.steps)])
        return reloaded_process