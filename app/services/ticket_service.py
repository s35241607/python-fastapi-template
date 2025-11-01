from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.enums import TicketStatus
from app.models.label import Label
from app.models.ticket import Ticket
from app.repositories.category_repository import CategoryRepository
from app.repositories.label_repository import LabelRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.response import PaginationResponse
from app.schemas.ticket import (
    TicketAssigneeUpdate,
    TicketCreate,
    TicketDescriptionUpdate,
    TicketLabelsUpdate,
    TicketQueryParams,
    TicketRead,
    TicketTitleUpdate,
    TicketUpdate,
)


class TicketService:
    def __init__(
        self,
        ticket_repo: TicketRepository = Depends(TicketRepository),
        category_repo: CategoryRepository = Depends(CategoryRepository),
        label_repo: LabelRepository = Depends(LabelRepository),
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

    async def get_tickets(
        self,
        query: TicketQueryParams,
        current_user_id: int,
    ) -> PaginationResponse[TicketRead]:
        """
        取得分頁工單列表，支援篩選與排序，回傳 PaginationResponse 結構
        """
        # pagination will be handled by repository with page/page_size
        # sorting handled by the repository using the passed query
        # let repository extract filters, pagination and sorting from the pydantic query
        # Repository now returns PaginationResponse[TicketRead]
        paginated = await self.ticket_repo.get_paginated(
            query=query,
            options=[selectinload(Ticket.categories), selectinload(Ticket.labels)],
        )
        # Ensure items are validated into TicketRead (repo returns converted ReadSchemaType)
        # The repository returns PaginationResponse[ReadSchemaType], which is compatible with TicketRead
        return paginated

    async def get_ticket_by_id(self, ticket_id: int, current_user_id: int) -> TicketRead:
        """
        以 ID 取得單一工單；若不存在則回傳 404。

        Business logic (如權限檢查)應該放在此層（目前僅處理不存在的情況）。
        """
        ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        # repository 已經會回傳 ReadSchemaType（若 auto_convert 開啟），但為保險起見，確保回傳 TicketRead
        return TicketRead.model_validate(ticket, from_attributes=True)

    async def get_ticket_by_ticket_no(self, ticket_no: str, current_user_id: int) -> TicketRead:
        """
        以 ticket_no 取得單一工單；若不存在則回傳 404。

        為了同時載入關聯（categories/labels），先透過 ticket_no 找到 id，然後以 get_by_id 帶 preload 撈取完整資料。
        """
        ticket = await self.ticket_repo.get_by_ticket_no(
            ticket_no, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return TicketRead.model_validate(ticket, from_attributes=True)

    async def update_ticket(self, ticket_id: int, ticket_update: TicketUpdate, current_user_id: int) -> TicketRead:
        """更新工單

        業務規則：
        - 僅票據建立者可編輯
        - 若更新 category_ids/label_ids，需重新取得完整物件
        - 不允許透過此方法更改 status（需使用狀態轉換 endpoint）
        """
        # 1. 取得現有工單以驗證權限
        existing_ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        if not existing_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 2. 驗證編輯權限（僅建立者可編輯）
        if existing_ticket.created_by != current_user_id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this ticket",
            )

        # 3. 取得 category 和 label 的完整物件列表（若有提供）
        categories: list[Category] | None = None
        labels: list[Label] | None = None

        if ticket_update.category_ids is not None:
            categories = await self.category_repo.get_by_ids(ticket_update.category_ids)

        if ticket_update.label_ids is not None:
            labels = await self.label_repo.get_by_ids(ticket_update.label_ids)

        # 4. 建構 Ticket 物件進行更新
        ticket = Ticket(
            **ticket_update.model_dump(exclude={"category_ids", "label_ids"}, exclude_unset=True),
        )
        # 若有新的關聯，則設定
        if categories is not None:
            ticket.categories = categories
        if labels is not None:
            ticket.labels = labels

        # 5. 調用 repository 進行更新
        updated_ticket = await self.ticket_repo.update(
            ticket_id,
            ticket,
            user_id=current_user_id,
            preload=[Ticket.categories, Ticket.labels],
        )

        if not updated_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 6. 重新載入關聯資料
        final_ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        return TicketRead.model_validate(final_ticket, from_attributes=True)

    # ===== 私有共用方法 =====

    async def _get_ticket_for_update(self, ticket_id: int, current_user_id: int) -> Ticket:
        """取得工單並驗證更新權限（共用方法）"""
        ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 基本權限檢查：建立者可以修改
        # 使用 getattr 來避免 SQLAlchemy column 比較問題
        if getattr(ticket, "created_by", None) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this ticket",
            )
        return ticket

    async def _update_ticket_simple(
        self,
        ticket_id: int,
        update_data: dict[str, Any],
        current_user_id: int,
    ) -> TicketRead:
        """更新工單（簡化版本）"""
        # 建構更新物件
        ticket = Ticket(**update_data)

        # 更新工單
        updated_ticket = await self.ticket_repo.update(
            ticket_id,
            ticket,
            user_id=current_user_id,
            preload=[Ticket.categories, Ticket.labels],
        )

        if not updated_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 重新載入關聯資料
        final_ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        return TicketRead.model_validate(final_ticket, from_attributes=True)

    # ===== 特定欄位更新方法 =====

    async def update_ticket_title(
        self,
        ticket_id: int,
        ticket_title_update: TicketTitleUpdate,
        current_user_id: int,
    ) -> TicketRead:
        """更新工單標題

        業務規則：
        - 建立者可以修改標題
        - 記錄 title_change 事件
        """
        # 驗證權限
        existing_ticket = await self._get_ticket_for_update(ticket_id, current_user_id)

        # 記錄舊值和新值（TODO: 之後實作事件記錄）
        event_details: dict[str, Any] = {
            "old_title": existing_ticket.title,
            "new_title": ticket_title_update.title,
        }

        # 更新標題
        return await self._update_ticket_simple(
            ticket_id=ticket_id,
            update_data=ticket_title_update.model_dump(),
            current_user_id=current_user_id,
        )

    async def update_ticket_description(
        self,
        ticket_id: int,
        ticket_description_update: TicketDescriptionUpdate,
        current_user_id: int,
    ) -> TicketRead:
        """更新工單描述

        業務規則：
        - 建立者可以修改描述
        - 記錄 description_change 事件
        """
        # 驗證權限
        existing_ticket = await self._get_ticket_for_update(ticket_id, current_user_id)

        # TODO: 記錄 description_change 事件

        # 更新描述
        return await self._update_ticket_simple(
            ticket_id=ticket_id,
            update_data=ticket_description_update.model_dump(),
            current_user_id=current_user_id,
        )

    async def update_ticket_labels(
        self,
        ticket_id: int,
        ticket_labels_update: TicketLabelsUpdate,
        current_user_id: int,
    ) -> TicketRead:
        """更新工單標籤

        業務規則：
        - 建立者可以修改標籤
        - 需要重新取得 label 物件列表
        - 記錄 labels_change 事件
        """
        # 驗證權限
        existing_ticket = await self._get_ticket_for_update(ticket_id, current_user_id)

        # 取得新的 label 物件列表
        labels = await self.label_repo.get_by_ids(ticket_labels_update.label_ids)

        # TODO: 記錄 labels_change 事件

        # 建構更新物件
        ticket = Ticket(labels=labels)

        # 更新工單
        updated_ticket = await self.ticket_repo.update(
            ticket_id,
            ticket,
            user_id=current_user_id,
            preload=[Ticket.categories, Ticket.labels],
        )

        if not updated_ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # 重新載入關聯資料
        final_ticket = await self.ticket_repo.get_by_id(
            ticket_id, include_deleted=False, options=[selectinload(Ticket.categories), selectinload(Ticket.labels)]
        )
        return TicketRead.model_validate(final_ticket, from_attributes=True)

    async def update_ticket_assignee(
        self,
        ticket_id: int,
        ticket_assignee_update: TicketAssigneeUpdate,
        current_user_id: int,
    ) -> TicketRead:
        """更新工單指派對象

        業務規則：
        - 建立者或管理員可以修改指派對象
        - 記錄 assignee_change 事件
        - 可能需要發送通知給新指派對象
        """
        # 驗證權限
        await self._get_ticket_for_update(ticket_id, current_user_id)

        # TODO: 記錄 assignee_change 事件

        # 更新指派對象
        return await self._update_ticket_simple(
            ticket_id=ticket_id,
            update_data=ticket_assignee_update.model_dump(),
            current_user_id=current_user_id,
        )

    async def update_ticket_status(self, ticket_id: int, status: TicketStatus, current_user_id: int) -> TicketRead:
        """更新工單狀態

        業務規則：
        - 狀態轉換有嚴格的業務規則
        - 只有特定角色可以更改狀態
        - 記錄 status_change 事件
        - 可能觸發通知或後續流程
        """
        # 驗證權限（狀態更改可能需要特殊權限）
        await self._get_ticket_for_update(ticket_id, current_user_id)

        # TODO: 實作狀態轉換規則

        # TODO: 記錄 status_change 事件

        # 更新狀態
        return await self._update_ticket_simple(
            ticket_id=ticket_id,
            update_data={"status": status},
            current_user_id=current_user_id,
        )
