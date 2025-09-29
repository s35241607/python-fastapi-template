from typing import cast

from fastapi import Depends
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.enums import TicketStatus
from app.models.label import Label
from app.models.ticket import Ticket
from app.repositories.category_repository import CategoryRepository
from app.repositories.label_repository import LabelRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead


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

    async def get_tickets(self) -> list[TicketRead]:
        """取得工單列表"""
        tickets = await self.ticket_repo.get_all(options=[selectinload(Ticket.categories), selectinload(Ticket.labels)])
        return cast(list[TicketRead], tickets)
