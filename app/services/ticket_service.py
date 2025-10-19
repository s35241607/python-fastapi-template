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
from app.schemas.ticket import TicketCreate, TicketQueryParams, TicketRead


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
