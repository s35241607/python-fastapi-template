from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from app.models.ticket import Ticket, TicketStatus
from app.repositories.base import BaseRepository

class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Ticket)

    async def get_ticket_with_details(self, ticket_id: int) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.user),
                selectinload(Ticket.comments).selectinload("user")
            )
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_tickets_by_user(self, user_id: int) -> List[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .options(selectinload(Ticket.comments))
            .where(Ticket.user_id == user_id)
        )
        return result.scalars().all()

    async def get_tickets_by_status(self, status: TicketStatus) -> List[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .options(selectinload(Ticket.user))
            .where(Ticket.status == status)
        )
        return result.scalars().all()

    async def get_all_with_details(self) -> List[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.user),
                selectinload(Ticket.comments).selectinload("user")
            )
        )
        return result.scalars().all()
