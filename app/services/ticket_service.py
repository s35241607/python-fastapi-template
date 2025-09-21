"""
Ticket Service
處理工單業務邏輯、狀態轉換驗證、通知等
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.models.enums import TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketSearchParams,
    TicketStatsResponse,
    TicketStatusUpdate,
    TicketUpdate,
)


class TicketService:
    """工單服務"""

    # 定義允許的狀態轉換
    ALLOWED_TRANSITIONS = {
        TicketStatus.DRAFT: [
            TicketStatus.WAITING_APPROVAL,
            TicketStatus.CANCELLED,
            TicketStatus.OPEN,  # 如果沒有審核流程
        ],
        TicketStatus.WAITING_APPROVAL: [
            TicketStatus.OPEN,  # 審核通過
            TicketStatus.REJECTED,
            TicketStatus.CANCELLED,
        ],
        TicketStatus.REJECTED: [
            TicketStatus.DRAFT,
            TicketStatus.CANCELLED,
        ],
        TicketStatus.OPEN: [
            TicketStatus.IN_PROGRESS,
            TicketStatus.RESOLVED,
            TicketStatus.CANCELLED,
        ],
        TicketStatus.IN_PROGRESS: [
            TicketStatus.RESOLVED,
            TicketStatus.OPEN,
            TicketStatus.CANCELLED,
        ],
        TicketStatus.RESOLVED: [
            TicketStatus.CLOSED,
            TicketStatus.IN_PROGRESS,
        ],
        TicketStatus.CLOSED: [],
        TicketStatus.CANCELLED: [],
    }

    def __init__(self, ticket_repository: TicketRepository):
        self.ticket_repository = ticket_repository

    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        user_id: int
    ) -> Tuple[bool, str, Optional[TicketResponse]]:
        """創建工單"""
        try:
            ticket = await self.ticket_repository.create_ticket(ticket_data, user_id)
            
            # TODO: 發送創建通知
            # await self._send_creation_notification(ticket)
            
            return True, "工單創建成功", TicketResponse.model_validate(ticket)
            
        except Exception as e:
            return False, f"工單創建失敗: {str(e)}", None

    async def get_ticket(
        self,
        ticket_id: int,
        user_id: int
    ) -> Tuple[bool, str, Optional[TicketResponse]]:
        """獲取工單詳情"""
        # 檢查訪問權限
        if not await self.ticket_repository.can_user_access_ticket(ticket_id, user_id):
            return False, "無權限訪問此工單", None

        ticket = await self.ticket_repository.get_with_relations(ticket_id)
        if not ticket:
            return False, "工單不存在", None

        return True, "獲取成功", TicketResponse.model_validate(ticket)

    async def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
        user_id: int
    ) -> Tuple[bool, str, Optional[TicketResponse]]:
        """更新工單"""
        # 檢查訪問權限
        if not await self.ticket_repository.can_user_access_ticket(ticket_id, user_id):
            return False, "無權限訪問此工單", None

        # 檢查是否可以編輯
        ticket = await self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return False, "工單不存在", None

        if not await self._can_user_edit_ticket(ticket, user_id):
            return False, "無權限編輯此工單", None

        try:
            updated_ticket = await self.ticket_repository.update_ticket(
                ticket_id, ticket_data, user_id
            )
            
            # TODO: 記錄變更日誌
            # await self._log_ticket_changes(ticket, updated_ticket, user_id)
            
            return True, "工單更新成功", TicketResponse.model_validate(updated_ticket)
            
        except Exception as e:
            return False, f"工單更新失敗: {str(e)}", None

    async def update_ticket_status(
        self,
        ticket_id: int,
        status_update: TicketStatusUpdate,
        user_id: int
    ) -> Tuple[bool, str, Optional[TicketResponse]]:
        """更新工單狀態"""
        # 檢查訪問權限
        if not await self.ticket_repository.can_user_access_ticket(ticket_id, user_id):
            return False, "無權限訪問此工單", None

        ticket = await self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return False, "工單不存在", None

        # 驗證狀態轉換
        if not self._is_valid_status_transition(ticket.status, status_update.status):
            return False, f"不允許從 {ticket.status} 轉換到 {status_update.status}", None

        # 檢查權限
        if not await self._can_user_change_status(ticket, status_update.status, user_id):
            return False, "無權限執行此狀態變更", None

        try:
            updated_ticket = await self.ticket_repository.update_status(
                ticket_id, status_update.status, user_id
            )
            
            # TODO: 記錄狀態變更
            # await self._log_status_change(ticket, status_update, user_id)
            
            # TODO: 發送狀態變更通知
            # await self._send_status_change_notification(ticket, status_update.status)
            
            return True, "狀態更新成功", TicketResponse.model_validate(updated_ticket)
            
        except Exception as e:
            return False, f"狀態更新失敗: {str(e)}", None

    async def search_tickets(
        self,
        search_params: TicketSearchParams,
        user_id: int,
        page: int = 1,
        size: int = 20
    ) -> Tuple[bool, str, Optional[TicketListResponse]]:
        """搜尋工單"""
        try:
            tickets, total = await self.ticket_repository.search_tickets(
                search_params, user_id, page, size
            )

            total_pages = (total + size - 1) // size

            response = TicketListResponse(
                items=[ticket for ticket in tickets],
                total=total,
                page=page,
                size=size,
                total_pages=total_pages,
            )

            return True, "搜尋成功", response
            
        except Exception as e:
            return False, f"搜尋失敗: {str(e)}", None

    async def get_ticket_stats(
        self,
        user_id: int
    ) -> Tuple[bool, str, Optional[TicketStatsResponse]]:
        """獲取工單統計"""
        try:
            stats = await self.ticket_repository.get_stats(user_id)
            
            response = TicketStatsResponse(**stats)
            return True, "統計獲取成功", response
            
        except Exception as e:
            return False, f"統計獲取失敗: {str(e)}", None

    async def delete_ticket(
        self,
        ticket_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """軟刪除工單"""
        # 檢查訪問權限
        if not await self.ticket_repository.can_user_access_ticket(ticket_id, user_id):
            return False, "無權限訪問此工單"

        ticket = await self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            return False, "工單不存在"

        # 檢查是否可以刪除
        if not await self._can_user_delete_ticket(ticket, user_id):
            return False, "無權限刪除此工單"

        # 檢查工單狀態是否允許刪除
        if ticket.status in [TicketStatus.IN_PROGRESS, TicketStatus.WAITING_APPROVAL]:
            return False, "當前狀態不允許刪除工單"

        try:
            await self.ticket_repository.soft_delete(ticket_id, user_id)
            
            # TODO: 記錄刪除日誌
            # await self._log_ticket_deletion(ticket, user_id)
            
            return True, "工單刪除成功"
            
        except Exception as e:
            return False, f"工單刪除失敗: {str(e)}"

    def _is_valid_status_transition(
        self,
        current_status: TicketStatus,
        new_status: TicketStatus
    ) -> bool:
        """驗證狀態轉換是否有效"""
        if current_status == new_status:
            return True
            
        allowed_statuses = self.ALLOWED_TRANSITIONS.get(current_status, [])
        return new_status in allowed_statuses

    async def _can_user_edit_ticket(self, ticket, user_id: int) -> bool:
        """檢查用戶是否可以編輯工單"""
        # 創建者可以編輯（除非已關閉或取消）
        if ticket.created_by == user_id:
            return ticket.status not in [TicketStatus.CLOSED, TicketStatus.CANCELLED]
        
        # 指派人可以編輯部分欄位
        if ticket.assigned_to == user_id:
            return ticket.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        # TODO: 檢查管理員權限
        return False

    async def _can_user_change_status(
        self,
        ticket,
        new_status: TicketStatus,
        user_id: int
    ) -> bool:
        """檢查用戶是否可以變更狀態"""
        # 創建者的權限
        if ticket.created_by == user_id:
            return new_status in [
                TicketStatus.WAITING_APPROVAL,
                TicketStatus.CANCELLED,
                TicketStatus.CLOSED,
            ]
        
        # 指派人的權限
        if ticket.assigned_to == user_id:
            return new_status in [
                TicketStatus.IN_PROGRESS,
                TicketStatus.RESOLVED,
                TicketStatus.OPEN,
            ]
        
        # TODO: 檢查審核人權限
        # TODO: 檢查管理員權限
        
        return False

    async def _can_user_delete_ticket(self, ticket, user_id: int) -> bool:
        """檢查用戶是否可以刪除工單"""
        # 只有創建者可以刪除
        if ticket.created_by == user_id:
            return True
        
        # TODO: 檢查管理員權限
        return False

    # TODO: 實作通知和日誌方法
    # async def _send_creation_notification(self, ticket):
    #     """發送創建通知"""
    #     pass
    
    # async def _send_status_change_notification(self, ticket, new_status):
    #     """發送狀態變更通知"""
    #     pass
    
    # async def _log_ticket_changes(self, old_ticket, new_ticket, user_id):
    #     """記錄工單變更"""
    #     pass
    
    # async def _log_status_change(self, ticket, status_update, user_id):
    #     """記錄狀態變更"""
    #     pass
    
    # async def _log_ticket_deletion(self, ticket, user_id):
    #     """記錄工單刪除"""
    #     pass